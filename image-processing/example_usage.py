#!/usr/bin/env python3
"""
Example usage of the Sugarcane Disease Classifier
"""

from inference import SugarcaneDiseaseClassifier

def main():
    # Initialize classifier with the trained model
    model_path = "best_model.pt"  # Path to your trained model
    classifier = SugarcaneDiseaseClassifier(model_path)

    # Example 1: Classify a single image
    image_path = "path/to/your/sugarcane_leaf.jpg"

    try:
        result = classifier.predict(image_path, top_k=3)  # Get top 3 predictions

        print("🖼️  Image Classification Result:")
        print(f"File: {result['image_path']}")
        print(f"🏆 Predicted Disease: {result['top_prediction']['class']}")
        print(f"📊 Confidence: {result['top_prediction']['confidence_percentage']}")

        print("\n📈 All Predictions:")
        for i, pred in enumerate(result['all_predictions'], 1):
            print(f"  {i}. {pred['class']}: {pred['confidence_percentage']}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure the image file exists.")

    # Example 2: Classify multiple images
    image_paths = [
        "path/to/image1.jpg",
        "path/to/image2.jpg",
        "path/to/image3.jpg"
    ]

    print("\n" + "="*50)
    print("Batch Classification Example:")
    print("="*50)

    # Filter out non-existent files
    valid_paths = [path for path in image_paths if os.path.exists(path)]

    if valid_paths:
        results = classifier.predict_batch(valid_paths, top_k=1)

        for result in results:
            if 'error' in result:
                print(f"❌ Error with {result['image_path']}: {result['error']}")
            else:
                filename = os.path.basename(result['image_path'])
                disease = result['top_prediction']['class']
                confidence = result['top_prediction']['confidence_percentage']
                print(f"✅ {filename}: {disease} ({confidence})")
    else:
        print("No valid image files found in the list.")

if __name__ == "__main__":
    import os
    main()