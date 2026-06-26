import psycopg2
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class DatabaseManager:
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "scraper_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logging.info("Database connection established successfully")
            return True
        except Exception as e:
            logging.error("Database connection failed: %s", str(e))
            print("Database connection error:", e)
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")

    def create_personal_data_table(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS personal_data (
                    id SERIAL PRIMARY KEY,
                    website_url VARCHAR(500) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    phone VARCHAR(50),
                    email VARCHAR(200),
                    address VARCHAR(500),
                    role VARCHAR(200),
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()
            cursor.close()
            logging.info("personal_data table created/verified")
            return True
        except Exception as e:
            logging.error("Error creating table: %s", str(e))
            print("Table creation error:", e)
            return False

    def save_personal_data(self, records):
        if not records:
            print("No data to save to database")
            return 0, 0
        if not self.connect():
            print("Could not connect to database")
            logging.warning("Database save skipped due to connection failure")
            return 0, 0
        self.create_personal_data_table()
        inserted = 0
        duplicates = 0
        try:
            cursor = self.conn.cursor()
            for record in records:
                try:
                    cursor.execute("""
                        INSERT INTO personal_data (website_url, name, phone, email, address, role, scraped_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        record.get("Website_URL", ""),
                        record.get("Name", ""),
                        record.get("Phone", ""),
                        record.get("Email", ""),
                        record.get("Address", ""),
                        record.get("Role", ""),
                        record.get("Scraped_At", "")
                    ))
                    self.conn.commit()
                    inserted += 1
                except Exception as e:
                    duplicates += 1
                    logging.warning("Duplicate or error: %s", e)
                    self.conn.rollback()
            cursor.close()
            print("Database:", inserted, "records inserted,", duplicates, "duplicates/errors")
            logging.info("Database insert: %s new, %s duplicates", inserted, duplicates)
        except Exception as e:
            logging.error("Error inserting data: %s", str(e))
            print("Insert error:", e)
            self.conn.rollback()
        finally:
            self.disconnect()
        return inserted, duplicates
