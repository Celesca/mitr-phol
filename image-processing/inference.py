import os
import argparse
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import timm
import json
from pathlib import Path

class SugarcaneDiseaseClassifier:
    def __init__(self, model_path: str, device: str = None):
        """
        Initialize the sugarcane disease classifier

        Args:
            model_path: Path to the saved model weights (.pt file)
            device: Device to run inference on ('cuda', 'cpu', or None for auto-detect)
        """
        # Configuration
        self.CLASS_NAMES = ["Healthy", "Mosaic", "RedRot", "Rust", "Yellow"]
        self.NUM_CLASSES = len(self.CLASS_NAMES)
        self.INPUT_SIZE = 224
        self.MODEL_NAME = "timm/convnextv2_tiny.fcmae"

        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"Using device: {self.device}")

        # Load model
        self.model = self._load_model(model_path)

        # Define transforms
        self.transform = transforms.Compose([
            transforms.Resize((self.INPUT_SIZE, self.INPUT_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_model(self, model_path: str):
        """Load the trained model"""
        # Create model architecture
        model = timm.create_model(
            self.MODEL_NAME,
            pretrained=False,  # Don't load pretrained weights
            num_classes=self.NUM_CLASSES
        )

        # Replace classifier with dropout (same as training)
        original_fc = model.head.fc
        model.head.fc = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(original_fc.in_features, self.NUM_CLASSES)
        )

        # Load trained weights
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        state_dict = torch.load(model_path, map_location=self.device)
        model.load_state_dict(state_dict)

        # Move to device and set to eval mode
        model = model.to(self.device)
        model.eval()

        print(f"Model loaded successfully from {model_path}")
        return model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """
        Preprocess a single image

        Args:
            image_path: Path to the image file

        Returns:
            Preprocessed image tensor
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Load and convert image
        image = Image.open(image_path).convert('RGB')

        # Apply transforms
        image_tensor = self.transform(image)

        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)

        return image_tensor.to(self.device)

    def predict(self, image_path: str, top_k: int = 1) -> dict:
        """
        Predict disease class for a single image

        Args:
            image_path: Path to the image file
            top_k: Number of top predictions to return

        Returns:
            Dictionary containing predictions
        """
        # Preprocess image
        image_tensor = self.preprocess_image(image_path)

        # Make prediction
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidences, predicted_classes = torch.topk(probabilities, top_k, dim=1)

        # Convert to CPU and numpy
        confidences = confidences.cpu().numpy()[0]
        predicted_classes = predicted_classes.cpu().numpy()[0]

        # Prepare results
        predictions = []
        for i in range(top_k):
            predictions.append({
                'class': self.CLASS_NAMES[predicted_classes[i]],
                'confidence': float(confidences[i]),
                'confidence_percentage': f"{confidences[i] * 100:.2f}%"
            })

        result = {
            'image_path': image_path,
            'top_prediction': predictions[0],
            'all_predictions': predictions,
            'model_info': {
                'model_name': self.MODEL_NAME,
                'num_classes': self.NUM_CLASSES,
                'input_size': self.INPUT_SIZE,
                'classes': self.CLASS_NAMES
            }
        }

        return result

    def predict_batch(self, image_paths: list, top_k: int = 1) -> list:
        """
        Predict disease classes for multiple images

        Args:
            image_paths: List of paths to image files
            top_k: Number of top predictions to return for each image

        Returns:
            List of prediction dictionaries
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path, top_k)
                results.append(result)
            except Exception as e:
                results.append({
                    'image_path': image_path,
                    'error': str(e)
                })

        return results


def main():
    parser = argparse.ArgumentParser(description='Sugarcane Leaf Disease Classification Inference')
    parser.add_argument('--model-path', type=str, default='best_model.pt',
                        help='Path to the trained model file (default: best_model.pt)')
    parser.add_argument('--image-path', type=str,
                        help='Path to the image file to classify')
    parser.add_argument('--image-dir', type=str,
                        help='Path to directory containing images to classify')
    parser.add_argument('--output', type=str,
                        help='Path to save results as JSON (optional)')
    parser.add_argument('--top-k', type=int, default=1,
                        help='Number of top predictions to show (default: 1)')
    parser.add_argument('--device', type=str, choices=['cpu', 'cuda'],
                        help='Device to run inference on (default: auto-detect)')

    args = parser.parse_args()

    # Validate arguments
    if not args.image_path and not args.image_dir:
        parser.error("Either --image-path or --image-dir must be specified")

    if args.image_path and args.image_dir:
        parser.error("Cannot specify both --image-path and --image-dir")

    # Initialize classifier
    try:
        classifier = SugarcaneDiseaseClassifier(args.model_path, args.device)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # Get image paths
    if args.image_path:
        image_paths = [args.image_path]
    else:
        # Get all image files from directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_paths = [
            str(f) for f in Path(args.image_dir).iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not image_paths:
            print(f"No image files found in {args.image_dir}")
            return

        print(f"Found {len(image_paths)} images in {args.image_dir}")

    # Make predictions
    results = classifier.predict_batch(image_paths, args.top_k)

    # Display results
    for result in results:
        if 'error' in result:
            print(f"\n❌ Error processing {result['image_path']}: {result['error']}")
            continue

        print(f"\n🖼️  Image: {os.path.basename(result['image_path'])}")
        print(f"🏆 Top Prediction: {result['top_prediction']['class']} "
              f"({result['top_prediction']['confidence_percentage']})")

        if args.top_k > 1:
            print("📊 All Predictions:")
            for i, pred in enumerate(result['all_predictions'], 1):
                print(f"  {i}. {pred['class']}: {pred['confidence_percentage']}")

    # Save results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {args.output}")


if __name__ == "__main__":
    main()