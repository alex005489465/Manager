import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'host': 'localhost',
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': 'manager_reviews_user',
    'password': os.getenv('MYSQL_USER_PASSWORD', 'your_password'),
    'database': 'manager_reviews_db',
    'charset': 'utf8mb4',
    'auth_plugin': 'caching_sha2_password'
}