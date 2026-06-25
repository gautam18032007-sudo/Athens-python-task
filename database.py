import psycopg2
from psycopg2.extras import execute_values
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename="scraper.log", level=logging.INFO,
                    format="%(asctime)s - %(message)s")


class DatabaseManager:
    """Manages PostgreSQL database operations for scraped data"""
    
    def __init__(self):
        """Initialize database connection using environment variables"""
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "scraper_db")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "password")
        self.conn = None
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
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
            logging.error(f"Database connection failed: {str(e)}")
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")
    
    def create_table(self):
        """Create books table if it doesn't exist"""
        try:
            cursor = self.conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                url VARCHAR(500) UNIQUE NOT NULL,
                category VARCHAR(200),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            cursor.execute(create_table_query)
            self.conn.commit()
            cursor.close()
            logging.info("Books table created/verified successfully")
            return True
        except Exception as e:
            logging.error(f"Error creating table: {str(e)}")
            print(f"Table creation error: {e}")
            return False
    
    def insert_books(self, books_data):
        """
        Insert scraped books data into database
        
        Args:
            books_data: List of dictionaries with keys: Title, URL, Category, Description
        
        Returns:
            Tuple of (success: bool, inserted_count: int, duplicate_count: int)
        """
        if not books_data:
            return True, 0, 0
        
        inserted_count = 0
        duplicate_count = 0
        
        try:
            cursor = self.conn.cursor()
            
            for book in books_data:
                try:
                    insert_query = """
                    INSERT INTO books (title, url, category, description)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE
                    SET updated_at = CURRENT_TIMESTAMP
                    """
                    cursor.execute(insert_query, (
                        book.get("Title", ""),
                        book.get("URL", ""),
                        book.get("Category", ""),
                        book.get("Description", "")
                    ))
                    inserted_count += 1
                except psycopg2.IntegrityError:
                    # URL already exists (duplicate)
                    duplicate_count += 1
                    self.conn.rollback()
                    continue
            
            self.conn.commit()
            cursor.close()
            
            logging.info(f"Database insert: {inserted_count} new records, {duplicate_count} duplicates")
            return True, inserted_count, duplicate_count
            
        except Exception as e:
            logging.error(f"Error inserting books: {str(e)}")
            print(f"Insert error: {e}")
            self.conn.rollback()
            return False, 0, 0
    
    def get_all_books(self):
        """Retrieve all books from database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, url, category, description FROM books ORDER BY id DESC")
            books = cursor.fetchall()
            cursor.close()
            return books
        except Exception as e:
            logging.error(f"Error retrieving books: {str(e)}")
            print(f"Retrieve error: {e}")
            return []
    
    def get_book_count(self):
        """Get total count of books in database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Exception as e:
            logging.error(f"Error getting book count: {str(e)}")
            return 0
    
    def delete_all_books(self):
        """Clear all books from database (for testing/reset)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM books")
            self.conn.commit()
            cursor.close()
            logging.info("All books deleted from database")
            return True
        except Exception as e:
            logging.error(f"Error deleting books: {str(e)}")
            return False
