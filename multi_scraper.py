import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename="multi_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =====================================================
# CONFIGURATION - Yahan websites add karo
# =====================================================
WEBSITES = [
    {
        "url": "https://example.com/contacts",
        "selectors": {
            "container": "div.person",
            "name": "h3.name",
            "phone": "span.phone",
            "email": "a.email",
            "address": "p.address"
        }
    },
    {
        "url": "https://example.com/people",
        "selectors": {
            "container": "div.person-card",
            "name": "h2.person-name",
            "phone": "span.phone-number",
            "email": "a.email-link",
            "address": "p.location"
        }
    }
]

# =====================================================
# MAIN SCRAPER FUNCTIONS
# =====================================================

def scrape_website(website_config):
    """
    Single website ko scrape karta hai
    
    Args:
        website_config: Dictionary with url and selectors
    
    Returns:
        List of dictionaries with extracted data
    """
    url = website_config["url"]
    selectors = website_config["selectors"]
    records = []
    
    try:
        print(f"\n🔄 Scraping: {url}")
        logging.info(f"Starting scrape of {url}")
        
        # Website se data download karo
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Container selector se sab records find karo
        containers = soup.select(selectors["container"])
        print(f"   Found {len(containers)} records")
        
        # Har record se data nikalo
        for idx, container in enumerate(containers):
            try:
                # Selectors ke hisaab se data extract karo
                name_elem = container.select_one(selectors["name"])
                phone_elem = container.select_one(selectors["phone"])
                email_elem = container.select_one(selectors["email"])
                address_elem = container.select_one(selectors["address"])
                
                record = {
                    "Website": url,
                    "Name": name_elem.get_text(strip=True) if name_elem else "N/A",
                    "Phone": phone_elem.get_text(strip=True) if phone_elem else "N/A",
                    "Email": email_elem.get_text(strip=True) if email_elem else "N/A",
                    "Address": address_elem.get_text(strip=True) if address_elem else "N/A",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                records.append(record)
                
            except Exception as e:
                logging.warning(f"Error extracting record {idx} from {url}: {e}")
                continue
        
        print(f"   ✓ Successfully scraped {len(records)} records")
        logging.info(f"Successfully scraped {len(records)} records from {url}")
        
    except requests.exceptions.Timeout:
        print(f"   ✗ Timeout error - Website respond nahi kiya")
        logging.error(f"Timeout error for {url}")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Network error: {e}")
        logging.error(f"Network error for {url}: {e}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        logging.error(f"Unexpected error for {url}: {e}")
    
    time.sleep(1)  # Rate limiting - server ko overload mat karo
    return records


def remove_duplicates(data):
    """Duplicate records remove karta hai"""
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Email ke basis pe duplicates hata do
    df_clean = df.drop_duplicates(subset=['Email', 'Phone'], keep='first')
    
    print(f"\n🧹 Duplicates removed: {len(df) - len(df_clean)}")
    logging.info(f"Duplicates removed: {len(df) - len(df_clean)}")
    
    return df_clean


def save_output(df, filename="bulk_output.csv"):
    """Data ko CSV file me save karta hai"""
    if df.empty:
        print("\n⚠️  No data found to save!")
        logging.warning("No data found to save")
        return False
    
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✓ Data saved to: {filename}")
        logging.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        print(f"\n✗ Error saving file: {e}")
        logging.error(f"Error saving file: {e}")
        return False


def display_summary(df):
    """Summary dikhata hai"""
    print("\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    print(f"Total records: {len(df)}")
    
    if not df.empty:
        print(f"Websites scraped: {df['Website'].nunique()}")
        print(f"Valid emails: {(df['Email'] != 'N/A').sum()}")
        print(f"Valid phones: {(df['Phone'] != 'N/A').sum()}")
        print("\n📋 Data Preview:")
        print(df.head(10).to_string(index=False))
    
    print("="*50 + "\n")


# =====================================================
# MAIN PROGRAM
# =====================================================

def main():
    """Main function - sab kuch yahan run hota hai"""
    
    print("\n" + "="*50)
    print("🚀 BULK WEBSITE SCRAPER")
    print("="*50)
    print(f"Starting time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("Scraper started")
    
    all_data = []
    
    # Har website ko scrape karo
    for website_config in WEBSITES:
        records = scrape_website(website_config)
        all_data.extend(records)
    
    # DataFrame banao
    df = pd.DataFrame(all_data)
    
    # Duplicates remove karo
    if not df.empty:
        df = remove_duplicates(df)
    
    # Output save karo
    save_output(df)
    
    # Summary dikhao
    display_summary(df)
    
    logging.info("Scraper completed")


if __name__ == "__main__":
    main()
