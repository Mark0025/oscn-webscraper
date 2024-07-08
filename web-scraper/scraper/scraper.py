import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from .document_processor import process_pdf, process_tiff

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.base_url = 'https://oscn.net/dockets/Results.aspx?db=oklahoma&dcct=7&FiledDateL='

    def scrape_table(self, date_str, output_file='output.csv'):
        print(f"Starting to scrape for date: {date_str}")
        url = self.base_url + date_str
        print(f"Sending GET request to URL: {url}")
        try:
            response = self.session.get(url, headers=self.headers)
            print(f"Response received. Status code: {response.status_code}")
            response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return
        except Exception as err:
            print(f'An error occurred: {err}')
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        print("Soup object created successfully.")
        
        table = soup.find('table', class_='caseCourtTable')
        if not table:
            raise ValueError("Table with specified class not found.")
        print("Table found successfully.")
        
        headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]
        print(f"Extracted headers: {headers}")
        rows = table.find_all('tr')[1:]
        data = [[td.text.strip() for td in row.find_all('td')] for row in rows]
        print(f"Extracted data: {data}")
        
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(output_file, index=False)
        print(f"Data saved to '{output_file}'.")

        # Extract document links and metadata
        self.extract_document_links_and_metadata(soup)

    def extract_document_links_and_metadata(self, soup):
        document_links = []
        for a in soup.find_all('a', href=True):
            if a['href'].endswith(('.pdf', '.tif', '.tiff')):
                document_links.append(a['href'])
        print(f"Extracted document links: {document_links}")

        for link in document_links:
            full_url = f"https://oscn.net{link}"
            print(f"Attempting to process document: {full_url}")
            try:
                if link.endswith('.pdf'):
                    process_pdf(full_url, self.session, self.headers)
                elif link.endswith(('.tif', '.tiff')):
                    process_tiff(full_url, self.session, self.headers)
            except Exception as e:
                print(f"Failed to process document: {full_url}. Error: {e}")
