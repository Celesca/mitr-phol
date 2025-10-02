# Sugarcane Leaf Disease Classification - Inference

This repository contains inference code for classifying sugarcane leaf diseases using a fine-tuned ConvNeXtV2 model.

## Model Information

- **Model**: ConvNeXtV2 Tiny (fine-tuned)
- **Classes**: 5 disease categories
  - Healthy
  - Mosaic
  - RedRot
  - Rust
  - Yellow
- **Input Size**: 224x224 pixels
- **Accuracy**: ~98% (based on training notebook)

## Setup

1. Install dependencies:
```bash
pip install -r requirements_inference.txt
```

2. Place your trained model file (`best_model.pt`) in the project directory.

## Testing the Setup

Run the test script to verify everything works:

```bash
python test_inference.py
```

This will:
- ✅ Check if the model file exists and can be loaded
- ✅ Test prediction with a dummy image
- ✅ Verify all components are working correctly

## Usage Examples

### Command Line Interface

#### Classify a single image:
```bash
python inference.py --image-path path/to/your/image.jpg
```

#### Classify all images in a directory:
```bash
python inference.py --image-dir path/to/images/folder/
```

#### Save results to JSON file:
```bash
python inference.py --image-path image.jpg --output results.json
```

#### Get top 3 predictions:
```bash
python inference.py --image-path image.jpg --top-k 3
```

#### Force CPU usage:
```bash
python inference.py --image-path image.jpg --device cpu
```

### Python API

```python
from inference import SugarcaneDiseaseClassifier

# Initialize classifier
classifier = SugarcaneDiseaseClassifier("best_model.pt")

# Classify single image
result = classifier.predict("path/to/image.jpg")
print(f"Predicted: {result['top_prediction']['class']}")
print(f"Confidence: {result['top_prediction']['confidence_percentage']}")

# Classify multiple images
results = classifier.predict_batch(["image1.jpg", "image2.jpg"])
for result in results:
    print(f"{result['image_path']}: {result['top_prediction']['class']}")
```

## Output Format

### Single Image Result:
```json
{
  "image_path": "path/to/image.jpg",
  "top_prediction": {
    "class": "Healthy",
    "confidence": 0.9876,
    "confidence_percentage": "98.76%"
  },
  "all_predictions": [
    {
      "class": "Healthy",
      "confidence": 0.9876,
      "confidence_percentage": "98.76%"
    }
  ],
  "model_info": {
    "model_name": "timm/convnextv2_tiny.fcmae",
    "num_classes": 5,
    "input_size": 224,
    "classes": ["Healthy", "Mosaic", "RedRot", "Rust", "Yellow"]
  }
}
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## Requirements

- Python 3.7+
- PyTorch 1.9+
- TorchVision 0.10+
- timm (PyTorch Image Models)
- Pillow

## Troubleshooting

1. **CUDA out of memory**: Use `--device cpu` to force CPU inference
2. **Model file not found**: Ensure `best_model.pt` is in the correct directory
3. **Import errors**: Install all requirements with `pip install -r requirements_inference.txt`
4. **Low confidence predictions**: The model may need more training data or the image quality might be poor

## Model Architecture

The model uses:
- ConvNeXtV2 Tiny backbone (pretrained on ImageNet)
- Custom classifier head with dropout
- Input normalization (ImageNet statistics)
- Trained with AdamW optimizer and cross-entropy loss