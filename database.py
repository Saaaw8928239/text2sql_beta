import psycopg2
from psycopg2 import sql, DatabaseError
from config import config
import pandas as pd

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        #Установка соединения с БД
        try:
            self.connection = psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            self.cursor = self.connection.cursor()
            print("Подключение к БД установлено успешно!")
            return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        #Закрытие соединения с БД
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Соединение с БД закрыто.")
    
    def execute_query(self, query, params=None, fetch=True):
        #Выполнение SQL-запроса с параметрами
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    # Для SELECT возвращаем результат
                    columns = [desc[0] for desc in self.cursor.description]
                    results = self.cursor.fetchall()
                    self.connection.commit()
                    return results, columns
                else:
                    # Для INSERT/UPDATE/DELETE
                    self.connection.commit()
                    return self.cursor.rowcount, None
            else:
                self.connection.commit()
                return None, None
                
        except DatabaseError as e:
            self.connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            raise e
    
    def get_table_structure(self, table_name='employees'):
        #Получение структуры таблицы (метаданные)
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchall()
    
    def get_sample_data(self, table_name='employees', limit=5):
        #Получение примеров данных из таблицы
        query = sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table_name))
        return self.execute_query(query, (limit,))

# Создаем глобальный экземпляр для использования во всем приложении
db = Database()

def init_db():
    #Инициализация БД при запуске приложения
    if db.connect():
        # Получаем структуру таблицы для NLP-модуля
        structure = db.get_table_structure()
        print("Структура таблицы employees:")
        for col in structure:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        return True
    return False