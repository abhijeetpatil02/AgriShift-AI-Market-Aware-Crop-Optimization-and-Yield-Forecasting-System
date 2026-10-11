import os

# Automatically load .env file if present
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'agrishift-super-secret-key-2026-prod')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('DB_PORT', 3306))
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_DB = os.environ.get('DB_NAME', 'agrishift_db')
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days
