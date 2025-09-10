import os
import gdown
from PyPDF2 import PdfReader

PDF_DIR = "pdf_resources"
os.makedirs(PDF_DIR, exist_ok=True)

def download_pdfs(ids_file="pdf_ids.txt"):
    """Downloads PDFs listed in ids_file from Google Drive."""
    files_ids = {}
    with open(ids_file, "r") as f:
        for line in f:
            if line.strip() and "," in line:
                name, file_id = line.strip().split(",", 1)
                files_ids[name.strip()] = file_id.strip()

    for name, file_id in files_ids.items():
        pdf_path = os.path.join(PDF_DIR, name)
        if not os.path.exists(pdf_path):
            url = f"https://drive.google.com/uc?id={file_id}"
            try:
                gdown.download(url, pdf_path, quiet=False)
                print(f"Downloaded {name}")
            except Exception as e:
                print(f"Error downloading {name}: {e}")
        else:
            print(f"{name} already exists, skipping download.")
    return [os.path.join(PDF_DIR, name) for name in files_ids.keys()]

def load_pdf(path):
    '''Loads text from a single PDF file.

    Args:
        path (str): The path to the PDF file.
    Returns:
        str: The extracted text from the PDF.       
    '''
    text = ""
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return text

def load_all_pdfs(pdf_paths):
    '''Loads text from multiple PDF files.

    Args:
        pdf_paths (list): A list of paths to the PDF files.
    Returns:
        str: The concatenated text from all PDFs, separated by newlines.
    '''
    texts = [load_pdf(path) for path in pdf_paths]
    return "\n".join(texts)
