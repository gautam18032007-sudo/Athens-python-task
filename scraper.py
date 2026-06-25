import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
from database import DatabaseManager


logging.basicConfig(filename="scraper.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

base_url = "https://books.toscrape.com/catalogue/page-{}.html"
total_pages = 5
wait_time = 0.5

# Initialize database manager
db_manager = DatabaseManager()


def get_page(url):
    try:
        r = requests.get(url, timeout=15)
        r.encoding = "utf-8"   
        return r.text
    except Exception as e:
        print("Error aaya:", e)
        logging.error("Error: " + str(e))
        return None



def extract_data(html):
    books = []
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("article", class_="product_pod")

    for item in items:
       
        a = item.find("h3").find("a")
        title = a["title"]

        
        link = "https://books.toscrape.com/catalogue/" + a["href"]

        
        category = ""
        description = ""
        page2 = get_page(link)
        if page2 is not None:
            soup2 = BeautifulSoup(page2, "html.parser")

            
            crumbs = soup2.find_all("li")
            if len(crumbs) >= 3:
                category = crumbs[2].get_text().strip()

            
            desc = soup2.find("div", id="product_description")
            if desc is not None:
                p = desc.find_next("p")
                description = p.get_text().strip()

        books.append({
            "Title": title,
            "URL": link,
            "Category": category,
            "Description": description
        })
        time.sleep(wait_time)

    return books



def save_to_csv(data):
    if not data:
        print("No data found")
        return pd.DataFrame()
    df = pd.DataFrame(data)

    
    df = df.drop_duplicates()
    df = df[df["Title"] != ""]

    df.to_csv("output.csv", index=False)
    return df


def save_to_database(data):
    """Save data to PostgreSQL database"""
    if not data:
        print("No data to save to database")
        return 0, 0
    
    # Connect to database
    if not db_manager.connect():
        print("Could not connect to database - skipping database save")
        logging.warning("Database save skipped due to connection failure")
        return 0, 0
    
    # Create table if needed
    db_manager.create_table()
    
    # Insert data
    success, inserted, duplicates = db_manager.insert_books(data)
    
    # Disconnect
    db_manager.disconnect()
    
    return inserted, duplicates


def main():
    logging.info("Scraper start hua")
    all_books = []
    pages_done = 0
    db_inserted = 0
    db_duplicates = 0

    
    for i in range(1, total_pages + 1):
        url = base_url.format(i)
        print("Page scrap kar rahe hain:", i)
        logging.info("Page scraping: " + url)

        html = get_page(url)
        if html is None:
            continue

        data = extract_data(html)
        all_books = all_books + data
        pages_done = pages_done + 1
        time.sleep(wait_time)

    # csv me save karo
    df = save_to_csv(all_books)
    
    # Database me save karo
    print("\nDatabase me save kar rahe hain...")
    db_inserted, db_duplicates = save_to_database(all_books)

    logging.info("Total pages: " + str(pages_done))
    logging.info("Total records scraped: " + str(len(all_books)))
    logging.info("CSV records saved: " + str(len(df)))
    logging.info("Database new records: " + str(db_inserted))
    logging.info("Database duplicates: " + str(db_duplicates))
    logging.info("Scraper khatam")

    print("\n----- SUMMARY -----")
    print("Pages scraped:", pages_done)
    print("Total records scraped:", len(all_books))
    print("CSV records saved:", len(df))
    print("Database new records:", db_inserted)
    print("Database duplicates:", db_duplicates)
    print("File: output.csv")
    print("Database: scraper_db (books table)")


if __name__ == "__main__":
    main()
