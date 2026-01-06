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
    """Initializes the MarkItDown engine with a resilient session."""
    session = Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (ConverterBot/1.0)"})
    return MarkItDown(requests_session=session)

md = get_md_engine()

# --- UI Components ---
st.title("📄 Universal File-to-Text")
st.markdown("Upload documents to extract clean Markdown and compare file savings.")

# [2] Upload Area
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
                # 1. Save to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # 2. Conversion Process
                with st.spinner("Processing..."):
                    result = md.convert(tmp_path)
                    markdown_content = result.text_content
                
                # 3. Calculate Converted Size
                converted_size_bytes = len(markdown_content.encode('utf-8'))
                converted_size_mb = converted_size_bytes / (1024 * 1024)
                
                # 4. Calculate Percentage reduction
                reduction = ((original_size_bytes - converted_size_bytes) / original_size_bytes) * 100

                # 5. UI Tabs
                tab1, tab2 = st.tabs(["📄 Preview & Download", "📊 File Size Comparison"])

                with tab1:
                    st.text_area("Markdown Preview", markdown_content, height=300, key=f"pre_{file_name}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button("Download .md", markdown_content, f"{base_name}_converted.md", "text/markdown", key=f"md_{file_name}")
                    with c2:
                        st.download_button("Download .txt", markdown_content, f"{base_name}_converted.txt", "text/plain", key=f"txt_{file_name}")

                with tab2:
                    # Create the comparison table
                    data = {
                        "File Version": ["Original File", "Converted Text"],
                        "Size": [f"{original_size_mb:.2f} MB", f"{converted_size_mb:.4f} MB"]
                    }
                    st.table(pd.DataFrame(data))
                    
                    # Show percentage reduction
                    st.info(f"💡 Text version is **{reduction:.1f}% smaller** than the original file.")

                # Cleanup temp file
                os.remove(tmp_path)

            except Exception as e:
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                # st.exception(e) # Uncomment this if you need to debug the specific error

else:
    st.info("Upload files to see the size comparison and preview.")

st.divider()
st.caption("Built with Microsoft MarkItDown | 2026 Edition")
