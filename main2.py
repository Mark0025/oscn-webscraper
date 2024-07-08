# Importing Libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import fitz  # PyMuPDF for PDF processing
from PIL import Image  # Pillow for image processing
import io
import logging
import pytesseract
import os

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.base_url = 'https://oscn.net/dockets/Results.aspx?db=oklahoma&dcct=7&FiledDateL='
        self.case_base_url = 'https://oscn.net/dockets/'
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.handler = logging.FileHandler('scraper.log')
        self.handler.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.data = []

    def scrape_table(self, date_str, output_file='output.csv'):
        self.logger.info(f"Starting to scrape for date: {date_str}")
        url = self.base_url + date_str
        self.logger.info(f"Sending GET request to URL: {url}")
        try:
            response = self.session.get(url, headers=self.headers)
            self.logger.info(f"Response received. Status code: {response.status_code}")
            response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f'HTTP error occurred: {http_err}')
            return
        except Exception as err:
            self.logger.error(f'An error occurred: {err}')
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        self.logger.info("Soup object created successfully.")
        
        table = soup.find('table', class_='caseCourtTable')
        if not table:
            self.logger.error("Table with specified class not found.")
            raise ValueError("Table with specified class not found.")
        self.logger.info("Table found successfully.")
        
        headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]
        self.logger.info(f"Extracted headers: {headers}")
        rows = table.find_all('tr')[1:]
        data = [[td.text.strip() for td in row.find_all('td')] for row in rows]
        self.data = pd.DataFrame(data, columns=headers)
        self.save_to_csv(output_file)

    def fetch_document(self, url):
        self.logger.info(f"Fetching document from URL: {url}")
        try:
            response = self.session.get(url, headers=self.headers)
            if response.status_code == 200:
                self.logger.info(f"Content of {url}:")
                self.parse_document(response.text)
            else:
                self.logger.error(f"Failed to fetch document from {url}")
        except Exception as e:
            self.logger.error(f"Error fetching document from {url}: {e}")

    def parse_document(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract case number
        case_number = soup.find('strong', string=lambda x: x and 'No.' in x)
        if case_number:
            case_number = case_number.get_text(strip=True).replace('No. ', '')
            self.logger.info(f"Case Number: {case_number}")
        
        # Extract filed date
        filed_date = soup.find('td', string=lambda x: x and 'Filed:' in x)
        if filed_date:
            filed_date = filed_date.find_next_sibling('td').get_text(strip=True)
            self.logger.info(f"Filed Date: {filed_date}")
        
        # Extract judge name
        judge = soup.find('td', string=lambda x: x and 'Judge:' in x)
        if judge:
            judge = judge.find_next_sibling('td').get_text(strip=True)
            self.logger.info(f"Judge: {judge}")
        
        # Extract document links
        doc_links = soup.find_all('a', class_=['doc-tif', 'doc-pdf'])
        for link in doc_links:
            doc_url = self.case_base_url + link['href']
            doc_format = link.get_text(strip=True)
            self.logger.info(f"Document ({doc_format}): {doc_url}")
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
                self.logger.error(f"Failed to download document from {url}")
        except Exception as e:
            self.logger.error(f"Error processing document from {url}: {e}")

    def extract_text_from_pdf(self, pdf_content):
        try:
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            self.logger.info(f"Text from PDF:\n{text}")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def extract_text_from_tiff(self, tiff_content):
        try:
            image = Image.open(io.BytesIO(tiff_content))
            text = pytesseract.image_to_string(image)
            self.logger.info(f"Text from TIFF:\n{text}")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from TIFF: {e}")
            return ""

    def save_to_csv(self, output_file):
        df = pd.DataFrame(self.data)
        try:
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                existing_df = pd.read_csv(output_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            else:
                self.logger.info(f"{output_file} does not exist or is empty. Creating a new file.")
        except FileNotFoundError:
            self.logger.info(f"{output_file} not found. Creating a new file.")
        except pd.errors.EmptyDataError:
            self.logger.info(f"{output_file} is empty. Creating a new file.")
        df.to_csv(output_file, index=False)
        self.logger.info(f"Data saved to {output_file}")

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_table('06-01-2024')
    target_url = 'https://www.oscn.net/dockets/GetCaseInformation.aspx?db=oklahoma&number=PB-2024-722&cmid=4319201'
    scraper.fetch_document(target_url)
    scraper.save_to_csv('outputs.csv')