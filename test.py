# Importing Libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

class Scraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        self.base_url = 'https://oscn.net/dockets/Results.aspx?db=oklahoma&dcct=7&FiledDateL='
        self.case_base_url = 'https://oscn.net/dockets/'
        self.output_folder = 'outputs'
        os.makedirs(self.output_folder, exist_ok=True)

    def scrape_table(self, date_str, output_file='output.csv'):
        print(f"Starting to scrape for date: {date_str}")
        url = self.base_url + date_str
        print(f"Sending GET request to URL: {url}")
        response = self.session.get(url, headers=self.headers)
        print("Response received. Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='caseCourtTable')
        if not table:
            raise ValueError("Table with specified class not found.")
        print("Table found. Processing...")
        
        headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]
        rows = table.find_all('tr')[1:]
        data = [[td.text.strip() for td in row.find_all('td')] for row in rows]
        
        df = pd.DataFrame(data, columns=headers)
        print(f"Saving data to CSV file: {output_file}")
        df.to_csv(output_file, index=False)
        print(f"Data saved to '{output_file}'.")

        case_links = [a['href'] for a in table.find_all('a', href=True)]
        case_data = []
        pdf_links = []
        for link in case_links:
            case_url = self.case_base_url + link
            print(f"Scraping case info from URL: {case_url}")
            case_info, pdfs = self.scrape_case_info(case_url)
            case_data.append(case_info)
            pdf_links.extend(pdfs)
        
        case_df = pd.DataFrame(case_data)
        print("Saving case details to CSV file: case_details.csv")
        case_df.to_csv('case_details.csv', index=False)
        print("Case details saved to 'case_details.csv'.")

        pdf_df = pd.DataFrame(pdf_links, columns=['PDF Links'])
        print("Saving PDF links to CSV file: pdf_links.csv")
        pdf_df.to_csv('pdf_links.csv', index=False)
        print("PDF links saved to 'pdf_links.csv'.")

    def scrape_case_info(self, url):
        print(f"Scraping case info from URL: {url}")
        response = self.session.get(url, headers=self.headers)
        print("Response received. Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        case_info = {
            'Case Number': soup.find('span', id='caseNumber').text.strip(),
            'Filed Date': soup.find('span', id='filedDate').text.strip(),
            'Parties': [party.text.strip() for party in soup.find_all('span', class_='partyName')],
        }
        print("Case info extracted.")
        
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if 'pdf' in link['href']:
                pdf_url = self.case_base_url + link['href']
                pdf_links.append(pdf_url)
                self.download_pdf(pdf_url)
        
        return case_info, pdf_links

    def download_pdf(self, url):
        print(f"Downloading PDF from URL: {url}")
        response = self.session.get(url, headers=self.headers)
        if response.status_code == 200:
            pdf_name = os.path.join(self.output_folder, url.split('/')[-1])
            with open(pdf_name, 'wb') as f:
                f.write(response.content)
            print(f"PDF saved to {pdf_name}")
        else:
            print(f"Failed to download PDF from {url}")

if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_table('06-01-2024')