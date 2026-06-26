import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime
from database import DatabaseManager

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

db_manager = DatabaseManager()


def get_urls_from_user():
    print("\nEnter URLs (one per line). Type 'done' when finished:")
    urls = []
    while True:
        url = input("Enter URL: ").strip()
        if url.lower() == "done":
            break
        if url.startswith("http://") or url.startswith("https://"):
            urls.append(url)
            print("Added:", url)
        else:
            print("Invalid URL - must start with http:// or https://")
    return urls


def scrape_website(url):
    records = []
    try:
        print("\nProcessing:", url)
        logging.info("Starting scrape of %s", url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        contact_elem = soup.select_one("h3.section-subheading.text-muted2")
        contact_text = contact_elem.get_text(separator="\n", strip=True) if contact_elem else ""
        lines = [line.strip() for line in contact_text.split("\n") if line.strip()]
        address = lines[0] if len(lines) > 0 else "N/A"
        phone = lines[1] if len(lines) > 1 else "N/A"
        email = lines[2] if len(lines) > 2 else "N/A"
        containers = soup.select("div.team-member")
        print("Found", len(containers), "records")
        for container in containers:
            try:
                name_elem = container.select_one("h4")
                role_elem = container.select_one("p.text-muted")
                record = {
                    "Website_URL": url,
                    "Name": name_elem.get_text(strip=True) if name_elem else "N/A",
                    "Phone": phone,
                    "Email": email,
                    "Address": address,
                    "Role": role_elem.get_text(strip=True) if role_elem else "N/A",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                records.append(record)
                print(" ", record["Name"], "-", record["Role"])
            except Exception as e:
                logging.warning("Error extracting record: %s", e)
        print("Scraped", len(records), "records from", url)
        logging.info("Scraped %s records from %s", len(records), url)
    except requests.exceptions.Timeout:
        print("Timeout - Website did not respond")
        logging.error("Timeout error for %s", url)
    except requests.exceptions.ConnectionError:
        print("Connection Error")
        logging.error("Connection error for %s", url)
    except requests.exceptions.RequestException as e:
        print("Network Error:", e)
        logging.error("Network error for %s: %s", url, e)
    except Exception as e:
        print("Error:", e)
        logging.error("Unexpected error for %s: %s", url, e)
    time.sleep(1)
    return records


def remove_duplicates(data):
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df_clean = df.drop_duplicates(subset=["Email", "Name"], keep="first")
    print("\nDuplicates removed:", len(df) - len(df_clean))
    logging.info("Duplicates removed: %s", len(df) - len(df_clean))
    return df_clean


def save_output(df, filename="output.csv"):
    if df.empty:
        print("\nNo data to save")
        logging.warning("No data found to save")
        return False
    try:
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print("\nData saved to CSV:", filename)
        logging.info("Data saved to %s", filename)
        return True
    except Exception as e:
        print("\nError saving CSV:", e)
        logging.error("Error saving CSV: %s", e)
        return False


def display_summary(df):
    print("\n" + "=" * 70)
    print("SCRAPING SUMMARY")
    print("=" * 70)
    if df.empty:
        print("No data scraped")
        return
    print("Total Records:", len(df))
    print("Websites Scraped:", df["Website_URL"].nunique())
    print("Valid Emails:", (df["Email"] != "N/A").sum())
    print("Valid Phones:", (df["Phone"] != "N/A").sum())
    print("Valid Addresses:", (df["Address"] != "N/A").sum())
    print("\n" + "-" * 70)
    print(df.to_string(index=False))
    print("=" * 70)


def main():
    print("\nPERSONAL DATA SCRAPER")
    print("Level 1: Scrape URLs | Level 2: Save to Database")
    print("Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("Scraper started")

    urls = get_urls_from_user()
    if not urls:
        print("No URLs entered. Exiting.")
        return

    print("\nProcessing", len(urls), "URL(s)...")
    all_data = []
    for url in urls:
        records = scrape_website(url)
        all_data.extend(records)

    df = pd.DataFrame(all_data)
    if not df.empty:
        df = remove_duplicates(df)

    save_output(df)

    print("\nSaving to database...")
    db_inserted, db_duplicates = db_manager.save_personal_data(df.to_dict("records"))

    display_summary(df)
    print("\nDatabase new records:", db_inserted)
    print("Database duplicates/errors:", db_duplicates)
    print("Completed:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info("Scraper completed successfully")


if __name__ == "__main__":
    main()
