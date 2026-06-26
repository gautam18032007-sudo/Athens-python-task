import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    filename="multi_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =====================================================
# CONFIGURATION - Websites जहाँ से data निकालना है
# =====================================================

WEBSITES = [
    {
        "name": "Example Business Directory",
        "url": "https://example.com/business-directory",
        "selectors": {
            "container": "div.business-card",
            "name": "h3.business-name",
            "phone": "span.phone-number",
            "email": "a.business-email",
            "address": "p.business-address"
        }
    },
    {
        "name": "Local Company List",
        "url": "https://example.com/companies",
        "selectors": {
            "container": "div.company",
            "name": "h2.company-title",
            "phone": "span.contact-phone",
            "email": "a.contact-email",
            "address": "div.company-location"
        }
    }
]

# =====================================================
# SCRAPER FUNCTIONS
# =====================================================

def scrape_website(website_config):
    """
    एक website को scrape करता है और data निकालता है
    """
    name = website_config.get("name", "Unknown")
    url = website_config["url"]
    selectors = website_config["selectors"]
    records = []
    
    try:
        print(f"\n🔄 Scraping: {name}")
        print(f"   URL: {url}")
        logging.info(f"Starting scrape of {name} - {url}")
        
        # Website से data download करो
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # सभी records को container से खोजो
        containers = soup.select(selectors["container"])
        print(f"   📍 Found {len(containers)} records")
        
        # हर record से data निकालो
        for idx, container in enumerate(containers, 1):
            try:
                # Selectors के हिसाब से data निकालो
                name_elem = container.select_one(selectors["name"])
                phone_elem = container.select_one(selectors["phone"])
                email_elem = container.select_one(selectors["email"])
                address_elem = container.select_one(selectors["address"])
                
                # Email को clean करो (link से)
                email_text = email_elem.get_text(strip=True) if email_elem else "N/A"
                if email_elem and email_elem.get("href"):
                    email_text = email_elem.get("href").replace("mailto:", "")
                
                record = {
                    "Website": name,
                    "URL": url,
                    "Name": name_elem.get_text(strip=True) if name_elem else "N/A",
                    "Phone": phone_elem.get_text(strip=True) if phone_elem else "N/A",
                    "Email": email_text,
                    "Address": address_elem.get_text(strip=True) if address_elem else "N/A",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                records.append(record)
                print(f"   ✓ Record {idx}: {record['Name']}")
                
            except Exception as e:
                logging.warning(f"Error extracting record {idx} from {name}: {e}")
                continue
        
        print(f"   ✅ Successfully scraped {len(records)} records")
        logging.info(f"Successfully scraped {len(records)} records from {name}")
        
    except requests.exceptions.Timeout:
        print(f"   ⏱️  Timeout - Website ne respond nahi kiya")
        logging.error(f"Timeout error for {name}")
    except requests.exceptions.ConnectionError:
        print(f"   🌐 Connection Error - Internet check karein")
        logging.error(f"Connection error for {name}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
        logging.error(f"Network error for {name}: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected Error: {e}")
        logging.error(f"Unexpected error for {name}: {e}")
    
    time.sleep(1)  # Rate limiting
    return records


def validate_data(record):
    """Check करता है कि record valid है या नहीं"""
    # कम से कम name और email होनी चाहिए
    if record["Name"] != "N/A" and record["Email"] != "N/A":
        return True
    return False


def remove_duplicates(data):
    """Duplicate records को हटाता है"""
    df = pd.DataFrame(data)
    
    if df.empty:
        return df
    
    # Email और Phone के basis पर duplicates हटाओ
    df_clean = df.drop_duplicates(subset=['Email', 'Name'], keep='first')
    
    duplicates_removed = len(df) - len(df_clean)
    print(f"\n🧹 Duplicates removed: {duplicates_removed}")
    logging.info(f"Duplicates removed: {duplicates_removed}")
    
    return df_clean


def save_output(df, filename="bulk_output.csv"):
    """Data को CSV file में save करता है"""
    if df.empty:
        print("\n⚠️  कोई data नहीं मिला!")
        logging.warning("No data found to save")
        return False
    
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n✅ Data saved to: {filename}")
        logging.info(f"Data saved to {filename}")
        return True
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")
        logging.error(f"Error saving file: {e}")
        return False


def save_json_output(df, filename="bulk_output.json"):
    """Data को JSON format में भी save करता है"""
    if df.empty:
        return False
    
    try:
        df.to_json(filename, orient='records', indent=2)
        print(f"✅ JSON also saved to: {filename}")
        logging.info(f"JSON data saved to {filename}")
        return True
    except Exception as e:
        logging.error(f"Error saving JSON: {e}")
        return False


def display_summary(df):
    """Summary दिखाता है"""
    print("\n" + "="*60)
    print("📊 SCRAPING SUMMARY REPORT")
    print("="*60)
    
    if df.empty:
        print("❌ कोई data नहीं मिला")
        return
    
    print(f"📈 Total Records: {len(df)}")
    print(f"🌐 Websites Scraped: {df['Website'].nunique()}")
    print(f"✉️  Valid Emails: {(df['Email'] != 'N/A').sum()}")
    print(f"📞 Valid Phones: {(df['Phone'] != 'N/A').sum()}")
    print(f"📍 Valid Addresses: {(df['Address'] != 'N/A').sum()}")
    
    print("\n" + "-"*60)
    print("📋 TOP 10 RECORDS PREVIEW:")
    print("-"*60)
    print(df.head(10).to_string(index=False))
    
    print("\n" + "-"*60)
    print("📊 STATISTICS BY WEBSITE:")
    print("-"*60)
    website_stats = df.groupby('Website').size()
    for website, count in website_stats.items():
        print(f"   • {website}: {count} records")
    
    print("\n" + "="*60)


def display_menu():
    """Menu दिखाता है"""
    print("\n" + "="*60)
    print("🚀 BULK WEBSITE SCRAPER - MAIN MENU")
    print("="*60)
    print("1. Start Scraping")
    print("2. View Configuration")
    print("3. Edit Websites (Manual)")
    print("4. Exit")
    print("="*60)
    
    choice = input("Choose option (1-4): ").strip()
    return choice


def view_config():
    """Configuration दिखाता है"""
    print("\n" + "="*60)
    print("⚙️  CURRENT CONFIGURATION")
    print("="*60)
    for idx, website in enumerate(WEBSITES, 1):
        print(f"\n{idx}. {website.get('name', 'Unknown')}")
        print(f"   URL: {website['url']}")
        print(f"   Selectors:")
        for key, value in website['selectors'].items():
            print(f"      • {key}: {value}")


# =====================================================
# MAIN PROGRAM
# =====================================================

def main():
    """Main function - सब कुछ यहाँ run होता है"""
    
    print("\n" + "="*60)
    print("🚀 BULK WEBSITE SCRAPER v2.0")
    print("="*60)
    print(f"⏰ Starting Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*60)
    logging.info("Scraper started")
    logging.info("="*60)
    
    all_data = []
    
    # हर website को scrape करो
    for website_config in WEBSITES:
        records = scrape_website(website_config)
        all_data.extend(records)
    
    # DataFrame बनाओ
    df = pd.DataFrame(all_data)
    
    # Duplicates हटाओ
    if not df.empty:
        df = remove_duplicates(df)
    
    # Output save करो
    save_output(df)
    save_json_output(df)
    
    # Summary दिखाओ
    display_summary(df)
    
    print(f"\n⏰ Completed Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("Scraper completed successfully")


if __name__ == "__main__":
    # Simple mode - directly start scraping
    main()
    
    # अगर menu चाहिए तो यह code uncomment करो:
    # while True:
    #     choice = display_menu()
    #     if choice == "1":
    #         main()
    #     elif choice == "2":
    #         view_config()
    #     elif choice == "3":
    #         print("Manual editing के लिए multi_scraper.py file को edit करो")
    #     elif choice == "4":
    #         print("👋 Goodbye!")
    #         break
    #     else:
    #         print("❌ Invalid choice")
