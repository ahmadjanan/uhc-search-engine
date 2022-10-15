import time
import logging

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec


CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


class UHCScraper:
    '''
    A Scraper to scrape all JSON URLs from UHC website. 
    '''
    def __init__(self, start_url):
        self.driver = webdriver.Chrome(options=CHROME_OPTIONS)
        self.start_url = start_url

    def extract_data(self):
        '''
        This functions extracts JSON files' URLs from webdriver's source page using BeautifulSoup.

        Returns
        -------
        hrefs: List
            List of scraped JSON files' URLs.
        '''

        hrefs = []
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        try:
            ul = soup.select('ul.ant-list-items')[0]
            logging.info('Webpage fully loaded. Scraping ...')
        except Exception as e:
            return

        hrefs = [a["href"] for a in ul.select("a[href]") if a['href'].endswith('index.json')]
        return hrefs

    def extract_company_data(self):
        '''
        This functions fetches the target webpage and waits for it to load before extracting JSON URLs.

        Returns
        -------
        links: List
            List of scraped JSON files' URLs.
        '''

        self.driver.get(self.start_url)
        WebDriverWait(self.driver, 50).until(ec.presence_of_element_located((By.CLASS_NAME, 'ant-space-item')))
        links = self.extract_data()
        while not links:
            logging.info('Webpage not fully loaded yet. Sleeping for 5 seconds ...')
            time.sleep(5)
            links = self.extract_data()

        return links


def main():
    '''
    Main function.
    '''
    
    start_url = 'https://transparency-in-coverage.uhc.com/'

    scraper = UHCScraper(start_url)
    logging.info('Scraper initialized.')
    logging.info('Fetching JSON files URLs.')
    company_data = scraper.extract_company_data()
    with open('company_files.txt', 'w') as f:
        f.write('\n'.join(company_data))

    logging.info(f'Fetched {len(company_data)} JSON files URLs.')
    scraper.driver.close()


if __name__ == '__main__':
    main()
