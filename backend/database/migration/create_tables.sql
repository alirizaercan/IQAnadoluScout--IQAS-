-- backend/database/migration/create_tables.sql
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    old_password VARCHAR(255),
    wrong_login_attempt INT DEFAULT 0,
    login_attempt INT DEFAULT 0,
    is_now_login VARCHAR(20) DEFAULT 'no',
    role VARCHAR(25),
    club VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
