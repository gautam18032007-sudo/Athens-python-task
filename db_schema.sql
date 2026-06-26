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

CREATE INDEX IF NOT EXISTS idx_personal_data_email ON personal_data(email);
CREATE INDEX IF NOT EXISTS idx_personal_data_name ON personal_data(name);
