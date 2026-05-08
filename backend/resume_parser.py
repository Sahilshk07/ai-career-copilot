"""
AI Career Copilot — Resume Parser Module
==========================================
Extracts text content from uploaded PDF resumes using pdfplumber.
Handles multi-page PDFs and provides clear error messages for
scanned/image-based documents that lack extractable text.

Author: Sahil Shaik
License: MIT
"""

import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pdfplumber.
    Returns the extracted text as a single string.
    """
    text_content = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    logger.warning(f"Could not extract text from page {i+1} of {pdf_path}")
        
        full_text = "\n".join(text_content).strip()
        
        if not full_text:
            raise ValueError("No extractable text found in the PDF. It might be a scanned image.")
            
        return full_text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise e
