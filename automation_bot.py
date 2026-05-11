import time
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnterpriseWebBot:
    """
    Automated Web Scraper and Interaction Bot using Selenium (Headless)
    """
    def __init__(self, headless=True):
        logging.info("Initializing Enterprise Web Bot...")
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--no-sandbox')
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            logging.info("WebDriver successfully started.")
        except WebDriverException as e:
            logging.error(f"Failed to initialize WebDriver: {e}")
            raise

    def fetch_page_data(self, url: str) -> list:
        """Navigates to a URL and extracts heading data."""
        logging.info(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(2)  # Wait for dynamic JS content to render
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        headings = soup.find_all(['h1', 'h2', 'h3'])
        
        extracted_data = [h.text.strip() for h in headings if h.text.strip()]
        logging.info(f"Extracted {len(extracted_data)} elements from the page.")
        return extracted_data

    def save_to_csv(self, data: list, filename: str = "extracted_data.csv"):
        """Saves extracted data to a CSV file using Pandas."""
        if not data:
            logging.warning("No data to save.")
            return
            
        df = pd.DataFrame(data, columns=["Extracted_Text"])
        df.to_csv(filename, index=False)
        logging.info(f"Data successfully saved to {filename}")

    def close_session(self):
        """Safely terminates the WebDriver session."""
        logging.info("Closing WebDriver session...")
        self.driver.quit()

if __name__ == "__main__":
    # Test Run
    target_url = "https://example.com"
    
    bot = EnterpriseWebBot(headless=True)
    try:
        data = bot.fetch_page_data(target_url)
        bot.save_to_csv(data)
    finally:
        bot.close_session()
