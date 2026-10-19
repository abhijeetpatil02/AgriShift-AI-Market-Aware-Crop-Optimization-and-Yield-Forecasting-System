"""
db.py
Database connection and repository layer supporting MySQL (via PyMySQL)
with automatic table initialization and resilient  fallback.
"""

import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from config import Config

# Track active driver
IS_MYSQL = False
DB_INIT_DONE = False

def get_mysql_connection(database=None):
    """Attempt connecting to MySQL server."""
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        port=Config.MYSQL_PORT,
        database=database,
        charset='utf8mb4',
        cursorclass=DictCursor,
        autocommit=True,
        connect_timeout=3
    )
    return conn

def get_sqlite_connection():
    """Fallback connection using SQLite."""
    conn = sqlite3.connect('agrishift.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables in MySQL, or falls back to SQLite if MySQL is unavailable."""
    global IS_MYSQL, DB_INIT_DONE
    
    # Try MySQL first
    try:
        # Step 1: Connect to server without database to create DB if needed
        server_conn = get_mysql_connection(database=None)
        with server_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        server_conn.close()

        # Step 2: Connect to the specific database
        conn = get_mysql_connection(database=Config.MYSQL_DB)
        with conn.cursor() as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(150) NOT NULL,
                    email VARCHAR(191) NOT NULL UNIQUE,
                    mobile VARCHAR(20) DEFAULT NULL,
                    user_type VARCHAR(50) DEFAULT 'Farmer',
                    state VARCHAR(100) DEFAULT 'Karnataka',
                    district VARCHAR(100) DEFAULT NULL,
                    preferred_language VARCHAR(20) DEFAULT 'en',
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Farm Profile table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farm_profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    land_area DECIMAL(10,2) DEFAULT NULL,
                    land_unit VARCHAR(20) DEFAULT 'Hectares',
                    primary_soil_type VARCHAR(100) DEFAULT NULL,
                    irrigation_source VARCHAR(100) DEFAULT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Prediction History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    district VARCHAR(100) NOT NULL,
                    season VARCHAR(50) NOT NULL,
                    farm_area_ha DECIMAL(10,2) NOT NULL,
                    nitrogen DECIMAL(8,2) DEFAULT NULL,
                    phosphorus DECIMAL(8,2) DEFAULT NULL,
                    potassium DECIMAL(8,2) DEFAULT NULL,
                    ph DECIMAL(4,2) DEFAULT NULL,
                    rainfall DECIMAL(8,2) DEFAULT NULL,
                    temperature DECIMAL(5,2) DEFAULT NULL,
                    humidity DECIMAL(5,2) DEFAULT NULL,
                    top_crop_1 VARCHAR(100) DEFAULT NULL,
                    crop1_yield DECIMAL(10,2) DEFAULT NULL,
                    crop1_revenue DECIMAL(14,2) DEFAULT NULL,
                    top_crop_2 VARCHAR(100) DEFAULT NULL,
                    crop2_yield DECIMAL(10,2) DEFAULT NULL,
                    crop2_revenue DECIMAL(14,2) DEFAULT NULL,
                    top_crop_3 VARCHAR(100) DEFAULT NULL,
                    crop3_yield DECIMAL(10,2) DEFAULT NULL,
                    crop3_revenue DECIMAL(14,2) DEFAULT NULL,
                    predicted_yield DECIMAL(10,2) DEFAULT NULL,
                    estimated_revenue DECIMAL(14,2) DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            # Ensure columns exist for all 3 crops in existing MySQL installations
            for col_name, col_type in [
                ('crop1_yield', 'DECIMAL(10,2) DEFAULT NULL'),
                ('crop1_revenue', 'DECIMAL(14,2) DEFAULT NULL'),
                ('crop2_yield', 'DECIMAL(10,2) DEFAULT NULL'),
                ('crop2_revenue', 'DECIMAL(14,2) DEFAULT NULL'),
                ('crop3_yield', 'DECIMAL(10,2) DEFAULT NULL'),
                ('crop3_revenue', 'DECIMAL(14,2) DEFAULT NULL')
            ]:
                try:
                    cursor.execute(f"ALTER TABLE prediction_history ADD COLUMN {col_name} {col_type};")
                except Exception:
                    pass

        conn.close()
        IS_MYSQL = True
        DB_INIT_DONE = True
        print(f"[*] Database successfully connected to MySQL ({Config.MYSQL_DB})")
        return True
    except Exception as e:
        print(f"[!] MySQL connection failed ({e}). Initializing SQLite fallback (agrishift.db)...")
        # Fallback to SQLite
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                mobile TEXT DEFAULT NULL,
                user_type TEXT DEFAULT 'Farmer',
                state TEXT DEFAULT 'Karnataka',
                district TEXT DEFAULT NULL,
                preferred_language TEXT DEFAULT 'en',
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farm_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                land_area REAL DEFAULT NULL,
                land_unit TEXT DEFAULT 'Hectares',
                primary_soil_type TEXT DEFAULT NULL,
                irrigation_source TEXT DEFAULT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                district TEXT NOT NULL,
                season TEXT NOT NULL,
                farm_area_ha REAL NOT NULL,
                nitrogen REAL DEFAULT NULL,
                phosphorus REAL DEFAULT NULL,
                potassium REAL DEFAULT NULL,
                ph REAL DEFAULT NULL,
                rainfall REAL DEFAULT NULL,
                temperature REAL DEFAULT NULL,
                humidity REAL DEFAULT NULL,
                top_crop_1 TEXT DEFAULT NULL,
                top_crop_2 TEXT DEFAULT NULL,
                top_crop_3 TEXT DEFAULT NULL,
                predicted_yield REAL DEFAULT NULL,
                estimated_revenue REAL DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        conn.commit()
        conn.close()
        IS_MYSQL = False
        DB_INIT_DONE = True
        print("[*] SQLite database ready.")
        return True

def get_db():
    """Get active DB connection."""
    global IS_MYSQL, DB_INIT_DONE
    if not DB_INIT_DONE:
        init_db()
    
    if IS_MYSQL:
        try:
            return get_mysql_connection(database=Config.MYSQL_DB)
        except Exception:
            # Revert to SQLite if MySQL dropped
            return get_sqlite_connection()
    else:
        return get_sqlite_connection()

# ----------------- User Queries -----------------

def get_user_by_email(email):
    """Fetch user dict by email."""
    conn = get_db()
    email_clean = email.strip().lower()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE LOWER(email) = %s LIMIT 1", (email_clean,))
                return cursor.fetchone()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ? LIMIT 1", (email_clean,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id):
    """Fetch user dict by id."""
    conn = get_db()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, full_name, email, mobile, user_type, state, district, preferred_language, created_at FROM users WHERE id = %s", (user_id,))
                return cursor.fetchone()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id, full_name, email, mobile, user_type, state, district, preferred_language, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def create_user(full_name, email, password_hash, mobile=None, user_type='Farmer', state='Karnataka', district=None, preferred_language='en'):
    """Create a new user account."""
    conn = get_db()
    email_clean = email.strip().lower()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (full_name, email, password_hash, mobile, user_type, state, district, preferred_language)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (full_name, email_clean, password_hash, mobile, user_type, state, district, preferred_language))
                return cursor.lastrowid
        else:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, mobile, user_type, state, district, preferred_language)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (full_name, email_clean, password_hash, mobile, user_type, state, district, preferred_language))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def save_prediction_history(user_id, district, season, farm_area_ha, nitrogen=None, phosphorus=None, potassium=None, ph=None, rainfall=None, temperature=None, humidity=None, top_crop_1=None, crop1_yield=None, crop1_revenue=None, top_crop_2=None, crop2_yield=None, crop2_revenue=None, top_crop_3=None, crop3_yield=None, crop3_revenue=None, predicted_yield=None, estimated_revenue=None):
    """Save prediction run with all 3 crops, yields, and revenues to history."""
    conn = get_db()
    # Ensure primary yield/revenue fallback to crop1
    p_yield = predicted_yield if predicted_yield is not None else crop1_yield
    e_rev = estimated_revenue if estimated_revenue is not None else crop1_revenue

    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO prediction_history (
                        user_id, district, season, farm_area_ha, nitrogen, phosphorus, potassium, ph,
                        rainfall, temperature, humidity,
                        top_crop_1, crop1_yield, crop1_revenue,
                        top_crop_2, crop2_yield, crop2_revenue,
                        top_crop_3, crop3_yield, crop3_revenue,
                        predicted_yield, estimated_revenue
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, district, season, farm_area_ha, nitrogen, phosphorus, potassium, ph,
                    rainfall, temperature, humidity,
                    top_crop_1, crop1_yield, crop1_revenue,
                    top_crop_2, crop2_yield, crop2_revenue,
                    top_crop_3, crop3_yield, crop3_revenue,
                    p_yield, e_rev
                ))
                return cursor.lastrowid
        else:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prediction_history (
                    user_id, district, season, farm_area_ha, nitrogen, phosphorus, potassium, ph,
                    rainfall, temperature, humidity,
                    top_crop_1, crop1_yield, crop1_revenue,
                    top_crop_2, crop2_yield, crop2_revenue,
                    top_crop_3, crop3_yield, crop3_revenue,
                    predicted_yield, estimated_revenue
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, district, season, farm_area_ha, nitrogen, phosphorus, potassium, ph,
                rainfall, temperature, humidity,
                top_crop_1, crop1_yield, crop1_revenue,
                top_crop_2, crop2_yield, crop2_revenue,
                top_crop_3, crop3_yield, crop3_revenue,
                p_yield, e_rev
            ))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def get_user_prediction_history(user_id, limit=20):
    """Retrieve history for a user."""
    conn = get_db()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM prediction_history
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT %s
                """, (user_id, limit))
                return cursor.fetchall()
        else:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM prediction_history
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    finally:
        conn.close()

def delete_prediction_history(history_id, user_id):
    """Delete a history record."""
    conn = get_db()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM prediction_history WHERE id = %s AND user_id = %s", (history_id, user_id))
                return cursor.rowcount > 0
        else:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM prediction_history WHERE id = ? AND user_id = ?", (history_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        conn.close()

# ----------------- Farm Profile Queries -----------------

def get_farm_profile(user_id):
    """Retrieve farm profile for a user."""
    conn = get_db()
    try:
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM farm_profiles WHERE user_id = %s LIMIT 1", (user_id,))
                res = cursor.fetchone()
                if res and 'land_area' in res and res['land_area'] is not None:
                    res['land_area'] = float(res['land_area'])
                return res
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM farm_profiles WHERE user_id = ? LIMIT 1", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            if 'land_area' in res and res['land_area'] is not None:
                res['land_area'] = float(res['land_area'])
            return res
    finally:
        conn.close()

def save_or_update_farm_profile(user_id, land_area, land_unit='Hectares', primary_soil_type=None, irrigation_source=None):
    """Create or update farm profile for a user."""
    conn = get_db()
    try:
        existing = get_farm_profile(user_id)
        if isinstance(conn, pymysql.connections.Connection):
            with conn.cursor() as cursor:
                if existing:
                    cursor.execute("""
                        UPDATE farm_profiles
                        SET land_area = %s, land_unit = %s, primary_soil_type = %s, irrigation_source = %s
                        WHERE user_id = %s
                    """, (land_area, land_unit, primary_soil_type, irrigation_source, user_id))
                    return existing['id']
                else:
                    cursor.execute("""
                        INSERT INTO farm_profiles (user_id, land_area, land_unit, primary_soil_type, irrigation_source)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, land_area, land_unit, primary_soil_type, irrigation_source))
                    return cursor.lastrowid
        else:
            cursor = conn.cursor()
            if existing:
                cursor.execute("""
                    UPDATE farm_profiles
                    SET land_area = ?, land_unit = ?, primary_soil_type = ?, irrigation_source = ?
                    WHERE user_id = ?
                """, (land_area, land_unit, primary_soil_type, irrigation_source, user_id))
                conn.commit()
                return existing['id']
            else:
                cursor.execute("""
                    INSERT INTO farm_profiles (user_id, land_area, land_unit, primary_soil_type, irrigation_source)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, land_area, land_unit, primary_soil_type, irrigation_source))
                conn.commit()
                return cursor.lastrowid
    finally:
        conn.close()

