import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# List of websites to scrape
websites = [
    "https://example.com/contacts",
    "https://example.com/people",
    "https://example.org/directory"
]

all_data = []

def scrape_website(url):
    """Simple function to scrape a single website"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all person records (adjust selector as needed)
        people = soup.find_all("div", class_="person")
        
        for person in people:
            # Extract data (modify selectors based on website structure)
            name = person.find("h3", class_="name")
            phone = person.find("span", class_="phone")
            email = person.find("a", class_="email")
            address = person.find("p", class_="address")
            
            data = {
                "Website": url,
                "Name": name.text.strip() if name else "N/A",
                "Phone": phone.text.strip() if phone else "N/A",
                "Email": email.text.strip() if email else "N/A",
                "Address": address.text.strip() if address else "N/A"
            }
            all_data.append(data)
        
        print(f"✓ Scraped {url} - Found {len(people)} people")
        
    except Exception as e:
        print(f"✗ Error scraping {url}: {e}")
    
    time.sleep(1)  # Wait before next request

# Scrape all websites
print("Starting bulk scraping...\n")
for website in websites:
    scrape_website(website)

# Save to CSV
df = pd.DataFrame(all_data)
df.to_csv("bulk_output.csv", index=False)

print(f"\n✓ Total records scraped: {len(all_data)}")
print(f"✓ Saved to: bulk_output.csv")
print("\nData Preview:")
print(df.head())
