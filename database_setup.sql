-- ============================================================
-- AgriPredict / AgriShift Database  Setup Script
-- Open and Execute this script in MySQL Workbench
-- ============================================================

-- 1. Create the Database
CREATE DATABASE IF NOT EXISTS `agrishift_db`
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Switch to the Database
USE `agrishift_db`;

-- 3. Create Users Table (Authentication & Profile)
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(191) NOT NULL UNIQUE,
    `mobile` VARCHAR(20) DEFAULT NULL,
    `user_type` VARCHAR(50) DEFAULT 'Farmer',
    `state` VARCHAR(100) DEFAULT 'Karnataka',
    `district` VARCHAR(100) DEFAULT NULL,
    `preferred_language` VARCHAR(20) DEFAULT 'en',
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Create Farm Profiles Table (Optional farm land metadata)
CREATE TABLE IF NOT EXISTS `farm_profiles` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `land_area` DECIMAL(10,2) DEFAULT NULL,
    `land_unit` VARCHAR(20) DEFAULT 'Hectares',
    `primary_soil_type` VARCHAR(100) DEFAULT NULL,
    `irrigation_source` VARCHAR(100) DEFAULT NULL,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_farm_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Create Prediction History Table (Saved AI forecasts)
CREATE TABLE IF NOT EXISTS `prediction_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `district` VARCHAR(100) NOT NULL,
    `season` VARCHAR(50) NOT NULL,
    `farm_area_ha` DECIMAL(10,2) NOT NULL,
    `nitrogen` DECIMAL(8,2) DEFAULT NULL,
    `phosphorus` DECIMAL(8,2) DEFAULT NULL,
    `potassium` DECIMAL(8,2) DEFAULT NULL,
    `ph` DECIMAL(4,2) DEFAULT NULL,
    `rainfall` DECIMAL(8,2) DEFAULT NULL,
    `temperature` DECIMAL(5,2) DEFAULT NULL,
    `humidity` DECIMAL(5,2) DEFAULT NULL,
    `top_crop_1` VARCHAR(100) DEFAULT NULL,
    `crop1_yield` DECIMAL(10,2) DEFAULT NULL,
    `crop1_revenue` DECIMAL(14,2) DEFAULT NULL,
    `top_crop_2` VARCHAR(100) DEFAULT NULL,
    `crop2_yield` DECIMAL(10,2) DEFAULT NULL,
    `crop2_revenue` DECIMAL(14,2) DEFAULT NULL,
    `top_crop_3` VARCHAR(100) DEFAULT NULL,
    `crop3_yield` DECIMAL(10,2) DEFAULT NULL,
    `crop3_revenue` DECIMAL(14,2) DEFAULT NULL,
    `predicted_yield` DECIMAL(10,2) DEFAULT NULL,
    `estimated_revenue` DECIMAL(14,2) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_history_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Verification Queries (Run these to confirm tables are created)
SHOW TABLES;
DESCRIBE `users`;
