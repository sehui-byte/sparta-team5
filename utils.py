import streamlit as st
import PyPDF2
import io
import os
from PIL import Image
import pytesseract
from pptx import Presentation

def display_job_description(job_details):
    """Display job description and requirements in a structured format"""
    # This function is now handled in app.py with HTML/CSS formatting
    pass

def validate_file(uploaded_file):
    """Validate if the uploaded file is a valid PDF, PPT, or image file"""
    file_type = uploaded_file.type
    try:
        if file_type == "application/pdf":
            PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            return True, "pdf"
        elif file_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            Presentation(io.BytesIO(uploaded_file.getvalue()))
            return True, "pptx"
        elif file_type in ["image/jpeg", "image/jpg", "image/png"]:
            Image.open(io.BytesIO(uploaded_file.getvalue()))
            return True, "image"
        else:
            return False, None
    except Exception as e:
        st.error(f"파일 검증 중 오류 발생: {str(e)}")
        return False, None

def extract_text_from_file(file_path, file_type):
    """Extract text content from a file based on its type"""
    try:
        text = ""
        
        if file_type == "pdf":
            # Extract text from PDF
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
        
        elif file_type == "pptx":
            # Extract text from PowerPoint
            prs = Presentation(file_path)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
        
        elif file_type == "image":
            # Extract text from image using OCR with Korean language support
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img, lang='kor+eng')
            except:
                # If pytesseract is not available or fails, provide a basic description
                text = "이미지 기반 이력서. 내용 추출을 위해 고급 OCR 기능이 필요합니다."
        
        return text
    except Exception as e:
        st.error(f"파일에서 텍스트 추출 중 오류 발생: {str(e)}")
        return None

def format_progress_bar(percentage):
    """Format a percentage into a progress bar for display"""
    if percentage < 0:
        percentage = 0
    if percentage > 100:
        percentage = 100
    
    return percentage / 100

def create_download_link(content, filename, text):
    """Create a download link for text content"""
    import base64
    encoded = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{encoded}" download="{filename}" class="download-btn">{text}</a>'
    return href
