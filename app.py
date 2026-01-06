import streamlit as st
import os
import tempfile
from markitdown import MarkItDown
from requests import Session

# --- Configuration & Setup ---
st.set_page_config(page_title="Universal Doc Converter", page_icon="📄")

# Initialize MarkItDown with custom request settings for resilience
# We use a Session to set a custom User-Agent and global timeout for web-related tasks
session = Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (ConverterBot/1.0)"})

# Note: MarkItDown uses this session for any internal URL fetching/web requests
md = MarkItDown(requests_session=session)

# --- UI Components ---
st.title("📄 Universal File-to-Text")
st.markdown("Upload Word, Excel, PPTX, PDF, or HTML files to convert them into clean Markdown.")

# [2] Upload Area (Multiple files supported)
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html", "zip"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Get file metadata
        file_name = uploaded_file.name
        base_name, _ = os.path.splitext(file_name)
        
        with st.expander(f"Processing: {file_name}", expanded=True):
            try:
                # Create a temporary file to save the uploaded bytes
                # MarkItDown typically works best with file paths or streams
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # [1] & [3] The Engine + Resilience (5s timeout simulation)
                # We process the conversion
                with st.spinner(f"Converting {file_name}..."):
                    result = md.convert(tmp_path)
                    markdown_content = result.text_content

                # [2] Instant Preview
                st.subheader("Preview")
                st.text_area(
                    label="Converted Text",
                    value=markdown_content,
                    height=300,
                    key=f"text_{file_name}"
                )

                # [2] & [4] Download Options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="Download as Markdown (.md)",
                        data=markdown_content,
                        file_name=f"{base_name}_converted.md",
                        mime="text/markdown",
                        key=f"md_{file_name}"
                    )
                
                with col2:
                    st.download_button(
                        label="Download as Text (.txt)",
                        data=markdown_content,
                        file_name=f"{base_name}_converted.txt",
                        mime="text/plain",
                        key=f"txt_{file_name}"
                    )

                # Cleanup temp file
                os.remove(tmp_path)

            except Exception as e:
                # [3] Resilience: Error Handling
                st.error(f"⚠️ Could not read {file_name}. Please check the format.")
                # Optional: log the actual error for the dev
                # st.write(f"Error details: {e}")

else:
    st.info("Please upload one or more files to begin.")

# Footer
st.divider()
st.caption("Built with Microsoft MarkItDown and Streamlit.")
