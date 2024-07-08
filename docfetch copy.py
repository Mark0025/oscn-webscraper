import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from io import BytesIO
import pandas as pd

class DocumentFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.base_url = 'https://www.oscn.net/dockets/'
        self.data = []

    def fetch_document(self, url):
        print(f"Fetching document from URL: {url}")
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            print(f"Content of {url}:")
            self.parse_document(response.text)
        else:
            print(f"Failed to fetch document from {url}")

    def parse_document(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract case number
        case_number = soup.find('strong', string=lambda x: x and 'No.' in x)
        if case_number:
            case_number = case_number.get_text(strip=True).replace('No. ', '')
            print(f"Case Number: {case_number}")
        
        # Extract filed date
        filed_date = soup.find('td', string=lambda x: x and 'Filed:' in x)
        if filed_date:
            filed_date = filed_date.find_next_sibling('td').get_text(strip=True)
            print(f"Filed Date: {filed_date}")
        
        # Extract judge name
        judge = soup.find('td', string=lambda x: x and 'Judge:' in x)
        if judge:
            judge = judge.find_next_sibling('td').get_text(strip=True)
            print(f"Judge: {judge}")
        
        # Extract document links
        doc_links = soup.find_all('a', class_=['doc-tif', 'doc-pdf'])
        for link in doc_links:
            doc_url = self.base_url + link['href']
            doc_format = link.get_text(strip=True)
            print(f"Document ({doc_format}): {doc_url}")
            self.process_document(doc_url, doc_format, case_number, filed_date, judge)

    def process_document(self, url, doc_format, case_number, filed_date, judge):
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                if doc_format == 'PDF':
                    text = self.extract_text_from_pdf(response.content)
                elif doc_format == 'TIFF':
                    text = self.extract_text_from_tiff(response.content)
                self.data.append({
                    'Case Number': case_number,
                    'Filed Date': filed_date,
                    'Judge': judge,
                    'Document URL': url,
                    'Document Format': doc_format,
                    'Extracted Text': text
                })
            else:
                print(f"Failed to download document from {url}")
        except Exception as e:
            print(f"Error processing document from {url}: {e}")

    def extract_text_from_pdf(self, pdf_content):
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            print(f"Text from PDF:\n{text}")
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_tiff(self, tiff_content):
        try:
            image = Image.open(BytesIO(tiff_content))
            text = pytesseract.image_to_string(image)
            print(f"Text from TIFF:\n{text}")
            return text
        except Exception as e:
            print(f"Error extracting text from TIFF: {e}")
            return ""

    def save_to_csv(self, output_file):
        df = pd.DataFrame(self.data)
        try:
            existing_df = pd.read_csv(output_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            pass
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")

if __name__ == "__main__":
    fetcher = DocumentFetcher()
    target_url = 'https://www.oscn.net/dockets/GetCaseInformation.aspx?db=oklahoma&number=PB-2024-722&cmid=4319201'
    fetcher.fetch_document(target_url)
    fetcher.save_to_csv('outputs.csv')