# Handwritten Text Recognition Tool

This application uses Azure Computer Vision service to convert handwritten text from images into digital text. It provides a simple web interface built with Streamlit.

## Features
- Upload images containing handwritten text
- Convert handwritten text to digital text
- Support for multiple image formats (JPG, JPEG, PNG, BMP)
- Download extracted text as a text file

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your Azure credentials:
```
AZURE_VISION_ENDPOINT=your_endpoint_here
AZURE_VISION_KEY=your_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage
1. Open the application in your web browser
2. Upload an image containing handwritten text
3. Click the "Extract Text" button
4. View the extracted text and download if needed

## Supported Image Formats
- JPG/JPEG
- PNG
- BMP

## Requirements
- Python 3.7+
- Streamlit
- Azure Cognitive Services Computer Vision API access
- Other dependencies listed in requirements.txt 