import streamlit as st
import os
import tempfile
import pandas as pd
from markitdown import MarkItDown
from requests import Session

# --- Configuration & Setup ---
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄", layout="wide")

@st.cache_resource
def get_md_engine():
    session = Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (ConverterBot/1.0)"})
    # Setting up MarkItDown with a resilient session
    return MarkItDown(requests_session=session)

md = get_md_engine()

# --- UI Components ---
st.title("📄 Universal File-to-Text")
st.markdown("Upload documents to instantly extract clean Markdown and compare file savings.")

uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html", "zip"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        base_name, _ = os.path.splitext(file_name)
        
        # Calculate Original Size
        original_size_bytes = uploaded_file.size
        original_size_mb = original_size_bytes / (1024 * 1024)

        with st.expander(f"📦 {file_name}", expanded=True):
            try:
                # Create a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # Conversion Engine
                with st.spinner("Processing..."):
                    result = md.convert(tmp_path)
                    markdown_content = result.text_content
                
                # Calculate Converted Size
                converted_size_bytes = len(markdown_content.encode('utf-8'))
                converted_size_mb = converted_size_bytes / (1024 * 1024)
                
                # Calculate Percentage reduction
                reduction = ((original_size_bytes - converted_size_bytes) / original_size_bytes) * 10
