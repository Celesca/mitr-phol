from crewai import LLM, Agent, Task, Crew
import os
import sys
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import timm

# Load environment variables
load_dotenv()

# Local classifier class (copied from inference.py)
class LocalClassifier:
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
        image_tensor = self._preprocess_image(image_path)

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

    def _preprocess_image(self, image_path: str) -> torch.Tensor:
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

from rag_tool import RAGSearchTool

class ImageProcessor:
    """Helper class to process images for local inference"""

    FALLBACK_IMAGE_URL = "https://storage.googleapis.com/kaggle-datasets-images/4320051/7424766/dd16b4fb7c01be6166e23cc348ae65ec/dataset-cover.jpeg?t=2024-01-18-04-10-18"

    @staticmethod
    def save_image_from_url(image_url: str, save_path: str) -> str:
        """Download image from URL and save to local path"""
        try:
            import requests
            response = requests.get(image_url)
            response.raise_for_status()

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save image
            with open(save_path, 'wb') as f:
                f.write(response.content)

            return save_path
        except Exception as e:
            raise Exception(f"Failed to download and save image: {str(e)}")

    @staticmethod
    def save_image_from_base64(base64_data: str, save_path: str) -> str:
        """Save base64 image data to local path"""
        try:
            import base64

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Decode and save
            image_data = base64.b64decode(base64_data)
            with open(save_path, 'wb') as f:
                f.write(image_data)

            return save_path
        except Exception as e:
            raise Exception(f"Failed to save base64 image: {str(e)}")

    @staticmethod
    def get_fallback_image(save_path: str) -> str:
        """Download and return the fallback image for testing"""
        try:
            return ImageProcessor.save_image_from_url(ImageProcessor.FALLBACK_IMAGE_URL, save_path)
        except Exception as e:
            raise Exception(f"Failed to download fallback image: {str(e)}")

class SugarcaneDiseaseClassifier:
    """Multi-agent system for sugarcane disease classification using local ViT model"""

    def __init__(self):
        # Initialize local classifier
        model_path = os.path.join(os.path.dirname(__file__), 'best_model.pt')
        try:
            self.local_classifier = LocalClassifier(model_path)
        except Exception as e:
            print(f"Warning: Could not load local classifier: {e}")
            self.local_classifier = None

        # Initialize RAG tool
        self.rag_tool = RAGSearchTool()

        # Initialize LLM for advice generation (using the same as Multi_agent.py)
        self.llm = LLM(
            model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            aws_region_name="us-east-1"
        )

        # Create specialized agents
        self.disease_analyzer = Agent(
            llm=self.llm,
            role="Disease Analysis Specialist",
            goal="Analyze disease classification results and provide detailed explanations",
            backstory="I am an expert in sugarcane diseases who can interpret classification results and explain what they mean for farmers.",
            verbose=True
        )

        self.treatment_advisor = Agent(
            llm=self.llm,
            role="Treatment and Prevention Advisor",
            goal="Provide practical treatment recommendations and prevention strategies",
            backstory="I am a sugarcane disease management expert who provides actionable advice for treating and preventing sugarcane diseases.",
            verbose=True
        )

    def classify_disease_from_image(self, image_path: str = None, user_description: str = "") -> str:
        """
        Classify sugarcane disease from image file path and user description

        Args:
            image_path: Path to the image file (optional - will use fallback if None)
            user_description: Optional text description from user

        Returns:
            Classification result with treatment recommendations
        """

        if not self.local_classifier:
            return "ขออภัยค่ะ ระบบจำแนกโรคไม่พร้อมใช้งาน กรุณาลองใหม่อีกครั้ง"

        try:
            # Handle case where no image is provided - use fallback
            if image_path is None or not os.path.exists(image_path):
                print("No image provided or image not found, using fallback image")
                # Create fallback image path
                fallback_dir = os.path.join(os.path.dirname(__file__), "fallback_images")
                os.makedirs(fallback_dir, exist_ok=True)
                import uuid
                fallback_filename = f"fallback_{uuid.uuid4()}.jpg"
                fallback_path = os.path.join(fallback_dir, fallback_filename)

                try:
                    image_path = ImageProcessor.get_fallback_image(fallback_path)
                    print(f"Downloaded fallback image to: {image_path}")
                except Exception as e:
                    print(f"Failed to download fallback image: {e}")
                    return "ขออภัยค่ะ ไม่สามารถโหลดรูปภาพสำหรับการทดสอบได้"

            # Use local classifier for disease classification
            classification_result = self.local_classifier.predict(image_path, top_k=3)

            # Format the classification result
            disease_info = self._format_classification_result(classification_result, user_description)

            # Get additional advice from RAG
            rag_query = f"โรคใบอ้อย {classification_result['top_prediction']['class']} อาการและการรักษา"
            rag_response = self.rag_tool._run(rag_query)

            # Combine results and generate comprehensive advice
            return self._generate_comprehensive_advice(disease_info, rag_response, user_description)

        except Exception as e:
            print(f"Error in disease classification: {e}")
            return f"ขออภัยค่ะ เกิดข้อผิดพลาดในการจำแนกโรค: {str(e)}"

    def _format_classification_result(self, result: dict, user_description: str = "") -> str:
        """Format the classification result into readable text"""
        top_pred = result['top_prediction']

        # Map English class names to Thai
        class_name_map = {
            "Healthy": "สุขภาพดี",
            "Mosaic": "โรคใบไหม้ (Mosaic)",
            "RedRot": "โรคแดงเน่า (Red Rot)",
            "Rust": "โรคสนิม (Rust)",
            "Yellow": "โรคใบเหลือง (Yellow Leaf)"
        }

        thai_class_name = class_name_map.get(top_pred['class'], top_pred['class'])

        formatted = f"ผลการจำแนกโรค: {thai_class_name}\n"
        formatted += f"ความมั่นใจ: {top_pred['confidence_percentage']}\n"

        if len(result['all_predictions']) > 1:
            formatted += "\nความเป็นไปได้อื่นๆ:\n"
            for i, pred in enumerate(result['all_predictions'][1:], 1):
                thai_name = class_name_map.get(pred['class'], pred['class'])
                formatted += f"{i}. {thai_name}: {pred['confidence_percentage']}\n"

        if user_description:
            formatted += f"\nคำอธิบายจากผู้ใช้: {user_description}\n"

        return formatted

    def _generate_comprehensive_advice(self, disease_info: str, rag_response: str, user_description: str = "") -> str:
        """Generate comprehensive advice using CrewAI with disease info and RAG knowledge"""

        # Task 1: Analyze the disease classification
        task1 = Task(
            description=f"""
            วิเคราะห์ผลการจำแนกโรคต่อไปนี้และให้คำอธิบายที่เข้าใจง่าย:

            {disease_info}

            ให้คำอธิบาย:
            1. โรคนี้คืออะไร
            2. อาการสำคัญที่เห็นได้
            3. สาเหตุของโรค
            4. ผลกระทบต่ออ้อย
            """,
            expected_output="คำอธิบายโรคที่เข้าใจง่ายในภาษาไทย",
            agent=self.disease_analyzer
        )

        # Task 2: Provide treatment recommendations using RAG knowledge
        task2 = Task(
            description=f"""
            จากข้อมูลการจำแนกโรคและความรู้เพิ่มเติม ให้คำแนะนำการรักษาและป้องกัน:

            ข้อมูลการจำแนก: {disease_info}

            ความรู้จากระบบ: {rag_response}

            ให้คำแนะนำที่ครอบคลุม:
            1. วิธีการรักษาทันที
            2. การป้องกันในอนาคต
            3. การจัดการแปลง
            4. แนวทางปฏิบัติที่ดี

            จัดรูปแบบให้เป็นข้อความที่อ่านง่ายและปฏิบัติได้จริง
            """,
            expected_output="คำแนะนำการรักษาและป้องกันที่ครอบคลุมในภาษาไทย",
            agent=self.treatment_advisor
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.disease_analyzer, self.treatment_advisor],
            tasks=[task1, task2],
            verbose=False,
            planning=False
        )

        result = crew.kickoff()

        # Extract the final result
        if hasattr(result, 'final_output'):
            return str(result.final_output)
        elif hasattr(result, 'output'):
            return str(result.output)
        elif hasattr(result, 'raw'):
            return str(result.raw)
        else:
            return str(result)

def process_sugarcane_image(image_path: str = None, user_description: str = "") -> str:
    """
    Main function to process sugarcane disease classification

    Args:
        image_path: Path to the image file (optional - will use fallback if None)
        user_description: User's text description

    Returns:
        Classification result and recommendations
    """
    classifier = SugarcaneDiseaseClassifier()
    return classifier.classify_disease_from_image(image_path, user_description)

# Example usage
if __name__ == "__main__":
    # Test with a sample image
    # result = process_sugarcane_image("path/to/image.jpg", "ใบเหลืองและมีจุด")
    # print(result)

    # Test with fallback image (no image_path provided)
    print("Testing with fallback image...")
    result = process_sugarcane_image(None, "ทดสอบระบบจำแนกโรคด้วยรูปภาพตัวอย่าง")
    print("Fallback test result:")
    print(result)

    print("Sugarcane Disease Classifier with local ViT model initialized.")