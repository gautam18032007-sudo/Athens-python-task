-- Database Schema for Books Scraper
-- Run this script to create the database and tables

-- Create database (if not exists)
-- Note: Run this separately if database doesn't exist:
-- createdb scraper_db

-- Create books table
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    category VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on URL for faster lookups
CREATE INDEX IF NOT EXISTS idx_books_url ON books(url);

-- Create index on category for filtering
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_books_created_at ON books(created_at DESC);
