import os

API_PORT = os.getenv('API_PORT', '5000')
API_IP = os.getenv('API_IP', '0.0.0.0')
API_DEBUG = os.getenv('API_DEBUG', True)

DB_IP = os.getenv('DB_IP', '192.168.37.50')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'project')

SHARED_SECRET = 'secret'