# pdf_extractor.py
import pypdf
import os
from typing import Union, Dict


# This is a helper function. It's used by our main tool but isn't a tool itself.
def _extract_text_from_single_pdf(pdf_path: str) -> Union[str, None]:
    """Internal function to load a single PDF and extract its text."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        return full_text
    except Exception:
        # We return None on any error to handle it gracefully in the main function.
        return None

# --- THE MAIN TOOL FUNCTION ---
def extract_text_from_pdfs_in_folder(folder_path: str) -> Dict[str, str]:
    """
    Scans a specified folder for PDF files, extracts text from each, and returns the content.

    Args:
        folder_path (str): The path to the directory containing the PDF files.
                           For example: 'pdf_files' or 'C:/Users/user/Documents/reports'.

    Returns:
        A dictionary where keys are the PDF filenames and values are the
        extracted text content as a single string. If a folder is not found or is empty,
        it returns an empty dictionary. If a PDF cannot be read, it will be skipped.
    """
    if not os.path.isdir(folder_path):
        # It's better to return a descriptive string for the AI to understand the error.
        return {"error": f"Folder '{folder_path}' not found."}

    all_pdf_texts = {}
    
    # List all files in the given directory
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            full_path = os.path.join(folder_path, filename)
            
            # Use the helper function to extract text
            text_content = _extract_text_from_single_pdf(full_path)
            
            if text_content:
                all_pdf_texts[filename] = text_content
            else:
                # Note that the file was processed but yielded no text
                all_pdf_texts[filename] = "[No text could be extracted. The file might be image-based or corrupted.]"

    return all_pdf_texts