# Website Data Scraper

Yeh ek Python program hai jo books.toscrape.com website se book ka data
nikaalta hai aur ek CSV file me save kar deta hai. Har book ka Title, URL,
Category aur Description nikala jaata hai. Program 5 pages se data collect
karta hai.

## Installation

- Python 3.11 ya usse upar install karein
- ek virtual environment banayein:
  - python -m venv venv
  - source venv/bin/activate   (Windows par: venv\Scripts\activate)
- libraries install karein:
  - pip install -r requirements.txt

requirements.txt me yeh libraries hain: requests, beautifulsoup4, pandas

## Kaise Run Karein

- virtual environment activate karke yeh command chalayein:
  - python scraper.py
- program chalne ke baad do files banengi:
  - output.csv  (saara data)
  - scraper.log (log file)

## Assumptions

- books.toscrape.com ek practice website hai isliye scraping allowed hai
- website ka structure same rahega (class names change nahi honge)
- internet connection chal raha hai

## Limitations

- code sirf books.toscrape.com ke liye banaya hai, dusri website par kaam nahi karega
- ek baar me ek hi page laata hai isliye thoda slow hai (around 1-2 minute)
- sirf Title, URL, Category aur Description nikalta hai
