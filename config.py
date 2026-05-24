import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    # Настройки подключения к PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'company_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Настройки Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'diploma-hr-system-secret-2026')
    DEBUG = False # Включать только при разработке
    
    # Настройки LLM и путей
    HISTORY_FILE = 'query_history.json'
    MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
    
    ABS_MIN_SALARY = 20000
    ABS_MAX_SALARY = 1000000

config = Config()