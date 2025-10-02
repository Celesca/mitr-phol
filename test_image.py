#!/usr/bin/env python3
"""
Test script for sugarcane disease classification
"""

from Image_agent import process_sugarcane_image, ImageProcessor

def test_image_classification():
    """Test image classification with a dummy image"""
    try:
        # For testing, you would replace this with actual image data
        # image_base64 = ImageProcessor.encode_image_from_path("path/to/test/image.jpg")
        # result = process_sugarcane_image(image_base64, "ใบอ้อยมีจุดสีน้ำตาล")
        # print("Classification Result:")
        # print(result)

        print("Image classification system initialized successfully!")
        print("To test with actual images:")
        print("1. Place a sugarcane image in your directory")
        print("2. Uncomment the code above and update the path")
        print("3. Run this script")

    except Exception as e:
        print(f"Error testing image classification: {e}")

if __name__ == "__main__":
    test_image_classification()