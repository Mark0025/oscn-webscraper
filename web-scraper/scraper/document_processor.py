import fitz  # PyMuPDF for PDF processing
from PIL import Image  # Pillow for image processing
import io
import requests  # Add this import

def process_pdf(url, session, headers):
    print(f"Attempting to fetch PDF: {url}")
    try:
        response = session.get(url, headers=headers)
        print(f"PDF response received. Status code: {response.status_code}")
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred while fetching PDF: {http_err}')
        return
    except Exception as err:
        print(f'An error occurred while fetching PDF: {err}')
        return
    
    pdf_document = fitz.open(stream=response.content, filetype="pdf")
    metadata = pdf_document.metadata
    print(f"PDF Metadata: {metadata}")
    # Extract text from PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        print(f"Page {page_num + 1} Text: {text}")

def process_tiff(url, session, headers):
    print(f"Attempting to fetch TIFF: {url}")
    try:
        response = session.get(url, headers=headers)
        print(f"TIFF response received. Status code: {response.status_code}")
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred while fetching TIFF: {http_err}')
        return
    except Exception as err:
        print(f'An error occurred while fetching TIFF: {err}')
        return
    
    image = Image.open(io.BytesIO(response.content))
    print(f"TIFF Image Info: {image.info}")
    # Extract text from TIFF using OCR if needed
    # For example, using pytesseract (not included in this code)
    # text = pytesseract.image_to_string(image)
    # print(f"TIFF Text: {text}")
