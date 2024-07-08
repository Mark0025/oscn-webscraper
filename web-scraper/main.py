# Importing Libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# In Python, we use the 'import' statement to bring in external libraries or modules that contain pre-written code. This allows us to use their functions and classes in our own code. Think of it like borrowing a tool from a friend to help you with a task.
# Here, we're importing three libraries:
# - requests: This library helps us send HTTP requests to websites and get their content.
# - BeautifulSoup: This library is a powerful tool for parsing HTML and XML documents, allowing for easy navigation and search capabilities within web page content. Some of the most common uses and use cases of BeautifulSoup include:
#   1. Web scraping: Gathering data from websites.
#   2. Data mining: Extracting specific data for business or research.
#   3. Web automation: Automating website tasks.
#   4. Content aggregation: Collecting content from multiple sites.
#   5. Monitoring website changes: Tracking website updates.
#   6. Data cleaning: Preprocessing extracted data.
#   7. Building datasets: Creating datasets for analysis or models.
#   8. Web crawling: Indexing website content.
#   9. Information retrieval: Finding specific website information.
#   10. Content analysis: Analyzing website content.
#   11. Sentiment analysis: Analyzing website text sentiment.
#   12. Topic modeling: Identifying website content themes.
#   13. Named entity recognition: Identifying people, places, and organizations.
#   14. Part-of-speech tagging: Identifying word types.
#   15. Language detection: Determining website language.
#   16. Text summarization: Summarizing website content.
#   17. Question answering: Answering questions from website content.
#   18. Machine translation: Translating website content.
#   19. Text classification: Categorizing website content.
#   20. Clustering: Grouping similar content.
# - pandas: This library provides data structures and functions to efficiently handle structured data, including tabular data such as spreadsheets and SQL tables. Some of the most common uses and use cases of pandas include:
#   1. Data cleaning: Preprocessing and cleaning up messy data.
#   2. Data exploration: Analyzing and understanding the structure of the data.
#   3. Data manipulation: Transforming and reshaping the data.
#   4. Data analysis: Performing statistical and other analyses on the data.
#   5. Data visualization: Creating visual representations of the data.
#   6. Time series analysis: Working with time series data.
#   7. Data aggregation: Combining data from multiple sources.
#   8. Data merging: Joining data from different sources.
#   9. Data filtering: Selecting a subset of the data based on certain criteria.
#   10. Data sorting: Arranging the data in a specific order.
#   11. Data grouping: Grouping the data based on certain criteria.
#   12. Data summarization: Creating summary statistics of the data.
#   13. Data transformation: Converting the data into a different format.
#   14. Data export: Saving the data to a file.
#   15. Data import: Loading the data from a file.
#   16. Data storage: Saving the data in a structured format for later use.
#   17. Data retrieval: Extracting the data from a database or other source.
#   18. Data validation: Checking the data for errors and inconsistencies.
#   19. Data normalization: Scaling the data to a common range.
#   20. Data imputation: Filling in missing values in the data.
# - datetime: This module supplies classes for manipulating dates and times.



# Defining a Class
# A class is a blueprint or a template that defines the characteristics and behaviors of an object.

# Simple Example: A Class with Only Attributes
# A class can have attributes, which are data that belongs to the class.
# class SimpleClass:
#     attribute1 = "value1"
#     attribute2 = "value2"

# Building on the Simple Example: A Class with a Method
# A class can also have methods, which are functions that belong to the class. These methods are used to perform actions that are specific to the class.
# In this example, we define a class called `ClassWithMethod` that has a method named `method1`. This method, when called, prints the message "This is a method".
# The `self` parameter in the `method1` definition is a reference to the current instance of the class and is used to access variables and methods from the class.
# It does not have to be named `self`, but it is a convention in Python to use `self` as the first parameter in a method definition.




# class ClassWithMethod:
#     def method1(self):
#         # Here, `self` refers to the instance of `ClassWithMethod` that this method is being called on.
#         print("This is a method")

# # Building on the Previous Example: A Class with an __init__ Method
# # The __init__ method is a special method that is automatically called when an object of the class is created.
# class ClassWithInit:
#     def __init__(self, attribute1, attribute2):
#         self.attribute1 = attribute1
#         self.attribute2 = attribute2

# # Building on the Previous Example: A Class with Multiple Methods
# # A class can have multiple methods that perform different actions.
# class ClassWithMultipleMethods:
#     def __init__(self, attribute1, attribute2):
#         self.attribute1 = attribute1
#         self.attribute2 = attribute2

#     def method1(self):
#         print("This is method 1")

#     def method2(self):
#         print("This is method 2")

# # Building on the Previous Example: A Class with Inheritance
# # A class can inherit the characteristics and behaviors of another class.
# class ParentClass:
#     def __init__(self, attribute1, attribute2):
#         self.attribute1 = attribute1
#         self.attribute2 = attribute2

# class ChildClass(ParentClass):
#     def __init__(self, attribute1, attribute2, attribute3):
#         super().__init__(attribute1, attribute2)
#         self.attribute3 = attribute3

class Scraper:
    def __init__(self):
        # The __init__ method is a special method that's automatically called when an object of this class is created. It sets up the initial state of the object.
        self.session = requests.Session()  # This creates a session object that allows us to persist certain parameters across requests.
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }  # This sets the User-Agent header to mimic a Firefox browser request.
        self.base_url = 'https://oscn.net/dockets/Results.aspx?db=oklahoma&dcct=7&FiledDateL='  # This is the base URL for the web scraping task.
        self.case_base_url = 'https://oscn.net/dockets/'

    def scrape_table(self, date_str, output_file='output.csv'):
        # This method scrapes a table from a web page based on a given date and saves the data to a CSV file.
        print(f"Starting to scrape for date: {date_str}")
        url = self.base_url + date_str  # Construct the full URL by appending the date to the base URL.
        print(f"Sending GET request to URL: {url}")
        response = self.session.get(url, headers=self.headers)  # Send a GET request to the URL with the specified headers.
        print("Response received. Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')  # Parse the HTML content of the page using BeautifulSoup.
        
        # Check if the table exists
        table = soup.find('table', class_='caseCourtTable')  # Find a table with the specified class. If not found, raise an error.
        if not table:
            raise ValueError("Table with specified class not found.")
        print("Table found. Processing...")
        
        # Process the table as before
        headers = [th.text.strip() for th in table.find_all('tr')[0].find_all('th')]  # Extract table headers.
        rows = table.find_all('tr')[1:]  # Skip the header row and get all other rows.
        data = [[td.text.strip() for td in row.find_all('td')] for row in rows]  # Extract data from each row.
        
        df = pd.DataFrame(data, columns=headers)  # Create a DataFrame from the data.
        print(f"Saving data to CSV file: {output_file}")
        df.to_csv(output_file, index=False)  # Save the DataFrame to a CSV file.
        print(f"Data saved to '{output_file}'.")

        # Extract hrefs and scrape additional data
        case_links = [a['href'] for a in table.find_all('a', href=True)]
        case_data = []
        for link in case_links:
            case_url = self.case_base_url + link
            print(f"Scraping case info from URL: {case_url}")
            case_info = self.scrape_case_info(case_url)
            case_data.append(case_info)
        
        case_df = pd.DataFrame(case_data)
        print("Saving case details to CSV file: case_details.csv")
        case_df.to_csv('case_details.csv', index=False)
        print("Case details saved to 'case_details.csv'.")

    def scrape_case_info(self, url):
        print(f"Scraping case info from URL: {url}")
        response = self.session.get(url, headers=self.headers)
        print("Response received. Parsing HTML content...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the required information from the case page
        # This is a placeholder; you need to adjust it based on the actual structure of the case page
        case_info = {
            'Case Number': soup.find('span', id='caseNumber').text.strip(),
            'Filed Date': soup.find('span', id='filedDate').text.strip(),
            'Parties': [party.text.strip() for party in soup.find_all('span', class_='partyName')],
            # Add more fields as needed
        }
        print("Case info extracted.")
        return case_info

if __name__ == "__main__":
    scraper = Scraper()  # Create an instance of the Scraper class.
    scraper.scrape_table('06-01-2024')