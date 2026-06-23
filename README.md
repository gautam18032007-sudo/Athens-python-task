# Website Data Scraper

Yeh Python scraper `books.toscrape.com` website se book data scrape karta hai aur usse `output.csv` file me save karta hai. Har record me book ka Title, URL, Category aur Description store kiya jata hai.

## Installation Steps

1. Virtual Environment create karein:

   ```
   python -m venv venv
   ```

2. Virtual Environment activate karein:

   ```
   venv\Scripts\activate
   ```

3. Required libraries install karein:

   ```
   pip install -r requirements.txt
   ```

## Run Karne Ka Tarika

```
python scraper.py
```

## Assumptions

* Website ka structure (HTML layout) change nahi hoga.
* Internet connection available hoga.
* Required Python libraries successfully install hongi.

## Limitations

* Scraper sirf pehle 5 pages scrape karta hai.
* Agar website down ho ya inaccessible ho to data collect nahi hoga.
* Website structure change hone par scraper fail ho sakta hai.
