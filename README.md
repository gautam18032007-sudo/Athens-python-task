# Personal Data Web Scraper

Yeh Python project websites se personal/team data scrape karta hai. Program run karte waqt terminal par multiple URLs enter kar sakte hain. Code har link ko ek-ek karke check karta hai, personal data nikalta hai, CSV file me save karta hai, aur PostgreSQL database me bhi store karta hai.

## Project Structure

| File | Level | Kaam |
|------|-------|------|
| `scraper.py` | Level 1 | URL input, web scraping, CSV output |
| `database.py` | Level 2 | PostgreSQL connection, table create, data insert |
| `db_schema.sql` | Level 2 | Database table ka SQL schema |
| `requirements.txt` | — | Required Python libraries |
| `.env.example` | — | Database configuration template |

## Scraped Data Fields

Har record me yeh fields store hote hain:

| Field | Description |
|-------|-------------|
| Website_URL | Kis website se data aaya |
| Name | Person ka naam |
| Phone | Phone number |
| Email | Email address |
| Address | Office/contact address |
| Role | Job title / designation |
| Scraped_At | Scrape karne ka date aur time |

## Workflow

```
python scraper.py
       ↓
Terminal par multiple URLs enter karo (type 'done' when finished)
       ↓
Har URL ek-ek karke check hoti hai
       ↓
Personal data extract hota hai (Name, Phone, Email, Address, Role)
       ↓
Duplicate records remove hote hain
       ↓
output.csv me save hota hai
       ↓
PostgreSQL me personal_data table create + data insert hota hai
       ↓
Terminal par summary report dikhta hai
```

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

4. Database configuration set karein:

   `.env.example` ko copy karke `.env` file banayein aur apne PostgreSQL credentials daalein:

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=scraper_db
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   ```

5. PostgreSQL database aur table create karein:

   ```
   createdb scraper_db
   psql -U postgres -d scraper_db -f db_schema.sql
   ```

## Run Karne Ka Tarika

```
python scraper.py
```

Example terminal input:

```
Enter URL: https://www.whiteathens.com/
Enter URL: done
```

## Output Files

| File | Description |
|------|-------------|
| `output.csv` | Scraped personal data (CSV format) |
| `scraper.log` | Program activity aur error logs |
| `personal_data` (DB table) | PostgreSQL me stored records |

## Database Table

`db_schema.sql` me `personal_data` table define hai:

- `id` — Auto increment primary key
- `website_url` — Source website URL
- `name` — Person name
- `phone` — Phone number
- `email` — Email address
- `address` — Address
- `role` — Job role
- `scraped_at` — Scrape timestamp
- `created_at` — Database insert timestamp

## Dependencies

- `requests` — Website pages download karne ke liye
- `beautifulsoup4` — HTML se data extract karne ke liye
- `pandas` — Data handling aur CSV export ke liye
- `psycopg2-binary` — PostgreSQL database connection ke liye
- `python-dotenv` — Environment variables load karne ke liye

## Assumptions

- Website ka HTML structure (team member sections) change nahi hoga.
- Internet connection available hoga.
- PostgreSQL server installed aur running hoga (Level 2 ke liye).
- Enter ki gayi URLs `http://` ya `https://` se start hongi.

## Limitations

- Scraper specific HTML structure par depend karta hai (`div.team-member`, contact section).
- Agar website down ho ya inaccessible ho to us URL ka data collect nahi hoga.
- Website structure change hone par scraper fail ho sakta hai.
- Agar database connect na ho to scraping aur CSV save phir bhi kaam karega, lekin database save skip ho jayega.
