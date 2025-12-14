import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env файла

class Config:
    # Настройки подключения к PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'company_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    # Формируем строку подключения
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Секретный ключ для Flask (сгенерировать можно так: import secrets; secrets.token_hex(16))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-123')
    
    # Настройки NLP
    SUPPORTED_DEPARTMENTS = ['IT', 'Маркетинг', 'Финансы', 'Продажи', 'HR', 'Логистика', 'Закупки', 'Руководство']
    MIN_SALARY = 50000
    MAX_SALARY = 500000

# Создаем экземпляр конфигурации
config = Config()