import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import logging
from typing import List, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class EnterpriseWebScraper:
    """
    Enterprise-grade web scraper with session management, retries, 
    and dynamic data extraction.
    """
    def __init__(self, base_url: str, output_prefix: str = "extracted_data"):
        self.base_url = base_url
        self.output_prefix = output_prefix
        self.data_buffer: List[Dict] = []
        self.session = self._configure_session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _configure_session(self) -> requests.Session:
        """Configures a robust requests session with connection pooling and retries."""
        session = requests.Session()
        # Automatically retry 3 times if server is down or rate-limited
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def extract_page_data(self, url: str) -> bool:
        """Extracts structured data from a single page with error handling."""
        logger.info(f"Initiating extraction for URL: {url}")
        try:
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Dynamic Extraction Logic (Targeting Quotes and Authors as a Demo)
            items = soup.find_all('div', class_='quote')
            if not items:
                logger.warning("No target elements found on the page. Stopping extraction.")
                return False
            
            for item in items:
                quote_text = item.find('span', class_='text').get_text(strip=True)
                author = item.find('small', class_='author').get_text(strip=True)
                tags = [tag.get_text(strip=True) for tag in item.find_all('a', class_='tag')]
                
                # Appending clean dictionary to buffer
                self.data_buffer.append({
                    "Quote": quote_text,
                    "Author": author,
                    "Tags": ", ".join(tags),
                    "Source_URL": url,
                    "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            logger.info(f"Successfully extracted {len(items)} records from current page.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during extraction: {e}")
            return False
        except Exception as e:
            logger.critical(f"Unexpected error in parsing logic: {e}")
            return False

    def export_data(self, format_type: str = 'csv') -> None:
        """Exports the buffered data into specified formats (CSV or JSON)."""
        if not self.data_buffer:
            logger.warning("Data buffer is empty. Nothing to export.")
            return
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_prefix}_{timestamp}.{format_type}"
        
        try:
            if format_type.lower() == 'csv':
                df = pd.DataFrame(self.data_buffer)
                df.to_csv(filename, index=False, encoding='utf-8')
                logger.info(f"Data successfully exported to CSV: {filename}")
            
            elif format_type.lower() == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.data_buffer, f, indent=4, ensure_ascii=False)
                logger.info(f"Data successfully exported to JSON: {filename}")
            
            else:
                logger.error(f"Unsupported export format: {format_type}")
                
        except IOError as e:
            logger.error(f"File I/O error during export: {e}")

def main():
    """Main execution block simulating an automated workflow."""
    logger.info("Starting Enterprise Automation Pipeline...")
    target_site = "http://quotes.toscrape.com/"
    
    # Initialize the Scraper
    scraper = EnterpriseWebScraper(base_url=target_site, output_prefix="scraped_dataset")
    
    # Simulating Multi-Page Pagination (Scraping first 5 pages automatically)
    for page_num in range(1, 6):  
        page_url = f"{target_site}page/{page_num}/"
        success = scraper.extract_page_data(page_url)
        
        if success:
            logger.info(f"Page {page_num} processed. Sleeping to respect server rate limits.")
            time.sleep(2)  # Polite scraping (Anti-bot detection bypass)
        else:
            logger.warning(f"Failed to process page {page_num}. Terminating loop.")
            break
            
    # Exporting data to both formats to show versatility
    logger.info("Executing Data Export Protocols...")
    scraper.export_data(format_type='csv')
    scraper.export_data(format_type='json')
    
    logger.info("Automation Pipeline Completed Successfully. Ready for production.")

if __name__ == "__main__":
    main()
