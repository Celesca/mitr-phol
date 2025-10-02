#!/usr/bin/env python3
"""
Test script to verify the inference setup works correctly
"""

import os
import torch
from inference import SugarcaneDiseaseClassifier

def test_model_loading():
    """Test if the model can be loaded successfully"""
    print("🔍 Testing model loading...")

    model_path = "best_model.pt"
    if not os.path.exists(model_path):
        print(f"⚠️  Model file '{model_path}' not found!")
        print("This is expected if you haven't trained the model yet.")
        print("To train the model, run the Jupyter notebook: 98-accuracy-w-fine-tuned-convnextv2.ipynb")
        print("The notebook will save the trained model as 'best_model.pt'")
        return False

    try:
        classifier = SugarcaneDiseaseClassifier(model_path)
        print("✅ Model loaded successfully!")
        print(f"📊 Model info: {classifier.NUM_CLASSES} classes, input size {classifier.INPUT_SIZE}x{classifier.INPUT_SIZE}")
        print(f"🏷️  Classes: {classifier.CLASS_NAMES}")
        return True
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_dummy_prediction():
    """Test prediction with a dummy tensor"""
    print("\n🔍 Testing dummy prediction...")

    try:
        classifier = SugarcaneDiseaseClassifier("best_model.pt")

        # Create a dummy RGB image tensor (3 channels, 224x224)
        dummy_image = torch.randn(3, 224, 224)

        # Save as temporary image for testing
        from PIL import Image
        import numpy as np

        # Convert tensor to PIL Image
        dummy_array = (dummy_image.numpy() * 255).astype(np.uint8).transpose(1, 2, 0)
        dummy_pil = Image.fromarray(dummy_array)
        dummy_pil.save("test_dummy_image.jpg")

        # Test prediction
        result = classifier.predict("test_dummy_image.jpg")

        print("✅ Dummy prediction successful!")
        print(f"🏆 Predicted class: {result['top_prediction']['class']}")
        print(f"📊 Confidence: {result['top_prediction']['confidence_percentage']}")

        # Clean up
        os.remove("test_dummy_image.jpg")

        return True
    except Exception as e:
        print(f"❌ Error in dummy prediction: {e}")
        return False

def main():
    print("🧪 Sugarcane Disease Classifier - Test Suite")
    print("=" * 50)

    # Test 1: Model Loading
    model_loaded = test_model_loading()

    if not model_loaded:
        print("\n❌ Test failed: Cannot proceed without model")
        return

    # Test 2: Dummy Prediction
    prediction_works = test_dummy_prediction()

    if prediction_works:
        print("\n🎉 All tests passed! The inference setup is working correctly.")
        print("\n💡 You can now use the classifier with real sugarcane leaf images:")
        print("   python inference.py --image-path your_image.jpg")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()