# Website Data Scraper
# yeh program books.toscrape.com se book ka data nikaalta hai
# aur output.csv file me save karta hai

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time

# logging setup - sab cheez scraper.log file me likhi jayegi
logging.basicConfig(filename="scraper.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")

base_url = "https://books.toscrape.com/catalogue/page-{}.html"
total_pages = 5
wait_time = 0.5


# yeh function website ka page laata hai
def get_page(url):
    try:
        r = requests.get(url, timeout=15)
        r.encoding = "utf-8"   # encoding set kar rahe hain price/text sahi dikhane ke liye
        return r.text
    except Exception as e:
        print("Error aaya:", e)
        logging.error("Error: " + str(e))
        return None


# yeh function ek page se saari books ka data nikaalta hai
def extract_data(html):
    books = []
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("article", class_="product_pod")

    for item in items:
        # title nikal rahe hain
        a = item.find("h3").find("a")
        title = a["title"]

        # book ka link banate hain
        link = "https://books.toscrape.com/catalogue/" + a["href"]

        # category aur description ke liye book ke page par jaana padta hai
        category = ""
        description = ""
        page2 = get_page(link)
        if page2 is not None:
            soup2 = BeautifulSoup(page2, "html.parser")

            # category breadcrumb me hoti hai
            crumbs = soup2.find_all("li")
            if len(crumbs) >= 3:
                category = crumbs[2].get_text().strip()

            # description ke liye
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


# data ko csv me save karta hai
def save_to_csv(data):
    df = pd.DataFrame(data)

    # data quality check - duplicate aur khaali rows hata rahe hain
    df = df.drop_duplicates()
    df = df[df["Title"] != ""]

    df.to_csv("output.csv", index=False)
    return df


def main():
    logging.info("Scraper start hua")
    all_books = []
    pages_done = 0

    # 5 pages se data lenge
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

    logging.info("Total pages: " + str(pages_done))
    logging.info("Total records: " + str(len(df)))
    logging.info("Scraper khatam")

    # summary print karte hain
    print("\n----- SUMMARY -----")
    print("Pages scraped:", pages_done)
    print("Total records:", len(all_books))
    print("Records saved:", len(df))
    print("File: output.csv")


main()
