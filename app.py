import streamlit as st
import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image
import time
from dotenv import load_dotenv
import io

# Set page configuration
st.set_page_config(
    page_title="Azure OCR Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    .main {
        padding: 0rem 1rem;
        font-family: 'Roboto', sans-serif;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(45deg, #00B4DB, #0083B0);
        color: white;
        border-radius: 10px;
        height: 3em;
        font-size: 1.2em;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #0083B0, #00B4DB);
    }
    
    .title-text {
        font-size: 4em !important;
        background: linear-gradient(120deg, #00B4DB, #0083B0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        padding: 0.2em 0;
        margin-bottom: 0.1em;
        animation: fadeIn 1.5s ease-in;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: -0.02em;
        line-height: 1.1;
        display: block;
    }
    
    .subtitle-text {
        font-size: 2em !important;
        color: #666;
        text-align: center;
        margin-bottom: 1.5em;
        animation: slideUp 1s ease-out;
        font-weight: 500;
        line-height: 1.2;
    }

    .section-header {
        font-size: 1.5em;
        color: #2C3E50;
        font-weight: 600;
        margin: 1em 0;
        padding-bottom: 0.3em;
        border-bottom: 2px solid #00B4DB;
    }
    
    .status-box {
        padding: 1em;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 5px solid #00B4DB;
        margin: 1em 0;
        animation: slideIn 0.5s ease-out;
        font-size: 1em;
    }
    
    .results-container {
        background-color: #f8f9fa;
        padding: 2em;
        border-radius: 10px;
        margin: 1em 0;
        border: 1px solid #e9ecef;
        animation: fadeIn 0.5s ease-in;
    }

    .results-container h3 {
        font-size: 2em;
        color: #2C3E50;
        margin-bottom: 0.8em;
    }
    
    .image-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1em 0;
        animation: scaleIn 0.5s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes scaleIn {
        from { transform: scale(0.95); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1.5em;
        border-radius: 10px;
        margin: 1em 0;
        border: 1px solid #e9ecef;
        font-size: 1.1em;
    }
    
    .status-success {
        color: #28a745;
        font-weight: 500;
        font-size: 1em;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: 500;
        font-size: 1.2em;
    }

    .tips-header {
        font-size: 1.5em;
        color: #2C3E50;
        margin-bottom: 0.5em;
    }

    .tips-content {
        font-size: 1.1em;
        line-height: 1.6;
    }

    .footer-text {
        font-size: 1.1em;
        color: #666;
        text-align: center;
        padding: 2em;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Azure credentials
endpoint = os.getenv('AZURE_VISION_ENDPOINT')
key = os.getenv('AZURE_VISION_KEY')

# Initialize the Computer Vision client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

def extract_text_from_image(image_bytes):
    try:
        # Create progress bar
        progress_text = "Operation in progress. Please wait..."
        progress_bar = st.progress(0)
        
        # Create BytesIO object from image bytes
        image_stream = io.BytesIO(image_bytes)
        
        # Submit the image for text recognition
        read_response = computervision_client.read_in_stream(image_stream, raw=True)
        
        if not read_response or 'Operation-Location' not in read_response.headers:
            progress_bar.empty()
            return "Error: Failed to get response from Azure. Please check your credentials."
            
        read_operation_location = read_response.headers["Operation-Location"]
        operation_id = read_operation_location.split("/")[-1]

        # Wait for the operation to complete
        progress = 0
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            progress += 0.1
            if progress > 0.9:
                progress = 0.9
            progress_bar.progress(progress)
            time.sleep(0.5)

        progress_bar.progress(1.0)
        time.sleep(0.5)
        progress_bar.empty()

        # Extract the text
        if read_result.status == OperationStatusCodes.succeeded:
            text = []
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    text.append(line.text)
            return "\n".join(text) if text else "No text was detected in the image."
        return "Text extraction failed."

    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return "An error occurred while processing the image."

def main():
    # Title with animation
    st.markdown('<p class="title-text">Azure Vision OCR</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Powered by Azure Computer Vision</p>', unsafe_allow_html=True)

    # Check Azure credentials
    if not endpoint or not key:
        st.error("🔑 Azure credentials not found. Please set AZURE_VISION_ENDPOINT and AZURE_VISION_KEY in your .env file.")
        return

    # Create two columns for layout
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### 📁 Upload Image")
        uploaded_file = st.file_uploader(
            "Supported formats: JPG, JPEG, PNG, BMP",
            type=["jpg", "jpeg", "png", "bmp"]
        )

        if uploaded_file:
            # Display upload success message
            st.markdown('<div class="status-box"><span class="status-success">✅ Image uploaded successfully!</span></div>', 
                       unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            with col2:
                st.markdown("### 📸 Preview")
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(image, caption="", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Add a button to trigger text extraction
            if st.button("🔍 Extract Text", key="extract_button"):
                with st.spinner("🔄 Processing image..."):
                    # Reset file pointer to the beginning
                    uploaded_file.seek(0)
                    # Get the bytes directly from the uploaded file
                    img_bytes = uploaded_file.read()
                    
                    # Extract text from the image
                    extracted_text = extract_text_from_image(img_bytes)
                    
                    # Display the results in a styled container
                    st.markdown('<div class="results-container">', unsafe_allow_html=True)
                    st.markdown("### 📝 Extracted Text:")
                    st.write(extracted_text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if extracted_text and extracted_text != "No text was detected in the image.":
                        # Add a download button for the extracted text
                        st.download_button(
                            label="💾 Download Text",
                            data=extracted_text,
                            file_name="extracted_text.txt",
                            mime="text/plain",
                            key="download_button"
                        )

        except Exception as e:
            st.error(f"⚠️ Error processing image: {str(e)}")

    # Add helpful tips in an expander
    with st.expander("💡 Tips for best results"):
        st.markdown("""
        - Use clear, well-lit images
        - Ensure text is clearly visible and not blurred
        - Avoid extreme angles
        - For best results, use high-resolution images
        - Make sure text is properly oriented
        """)

    # Add footer
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2em;'>
        <small>Made with ❤️ using Azure Computer Vision</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 