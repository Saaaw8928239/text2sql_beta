import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

class Config:
    # =====================================================
    # 1. Настройки подключения к PostgreSQL
    # =====================================================
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'company_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Строка подключения (для библиотек типа SQLAlchemy, если понадобятся)
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # =====================================================
    # 2. Настройки Flask
    # =====================================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'diploma-hr-system-secret-2026')
    DEBUG = False # Включать только при разработке
    
    # =====================================================
    # 3. Настройки LLM и путей
    # =====================================================
    # Путь к файлу истории запросов
    HISTORY_FILE = 'query_history.json'
    
    # Название используемой модели
    MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
    
   
    
    ABS_MIN_SALARY = 20000
    ABS_MAX_SALARY = 1000000

# Создаем экземпляр конфигурации для импорта в другие модули
config = Config()