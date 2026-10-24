-- =====================================================================
-- MUSCLE MONSTER GYM — MYSQL DATABASE SCHEMA
-- Database: muscle_monster_db
-- Table: users (Secure Authentication System)
-- =====================================================================

CREATE DATABASE IF NOT EXISTS muscle_monster_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE muscle_monster_db;

-- ---------------------------------------------------------------------
-- Table: users
-- Stores user identity, credentials (bcrypt hash), and timestamp
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(191) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    membership_tier VARCHAR(50) DEFAULT 'Standard Athlete',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
