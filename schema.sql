-- create database (run as mysql root or admin)
CREATE DATABASE IF NOT EXISTS mgnrega_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mgnrega_db;

-- districts table
CREATE TABLE IF NOT EXISTS districts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  state VARCHAR(100) NOT NULL,
  district_code VARCHAR(64) NOT NULL,
  district_name VARCHAR(200) NOT NULL,
  centroid_lat DOUBLE NULL,
  centroid_lon DOUBLE NULL,
  UNIQUE KEY uq_district_code (district_code)
);

-- monthly metrics table
CREATE TABLE IF NOT EXISTS monthly_metrics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  district_id INT NOT NULL,
  year INT NOT NULL,
  month INT NOT NULL,
  person_days BIGINT DEFAULT 0,
  households BIGINT DEFAULT 0,
  avg_wage DECIMAL(10,2) DEFAULT 0,
  beneficiaries BIGINT DEFAULT 0,
  other_json JSON NULL,
  source_updated_at DATETIME NULL,
  fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_district_month (district_id, year, month),
  CONSTRAINT fk_district FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
);

-- optional sync_log
CREATE TABLE IF NOT EXISTS sync_log (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_name VARCHAR(255),
  status VARCHAR(50),
  details TEXT,
  started_at DATETIME,
  finished_at DATETIME
);
