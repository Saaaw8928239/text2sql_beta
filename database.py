import psycopg2
from psycopg2 import sql, DatabaseError
from config import config

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Установка соединения с БД PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD
            )
            self.cursor = self.connection.cursor()
            print("✅ Подключение к PostgreSQL установлено успешно.")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        """Закрытие соединения с БД"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Соединение с БД закрыто.")
    
    def execute_query(self, query, params=None, fetch=True):
        """Выполнение SQL-запроса с возвратом данных и имен колонок"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if fetch:
                # Проверяем, является ли запрос выборкой данных
                upper_query = query.strip().upper()
                if upper_query.startswith('SELECT') or upper_query.startswith('WITH'):
                    # Извлекаем имена колонок для корректного отображения в таблице на фронтенде
                    columns = [desc[0] for desc in self.cursor.description]
                    results = self.cursor.fetchall()
                    return results, columns
                else:
                    self.connection.commit()
                    return self.cursor.rowcount, None
            else:
                self.connection.commit()
                return None, None
                
        except DatabaseError as e:
            if self.connection:
                self.connection.rollback()
            print(f"❌ Ошибка выполнения запроса: {e}")
            raise e
    
    def get_table_structure(self, table_name):
        """Получение структуры конкретной таблицы (колонки, типы данных)"""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position;
        """
        self.cursor.execute(query, (table_name,))
        return self.cursor.fetchall()

    def get_all_tables_metadata(self):
        """
        Получение метаданных всех таблиц HR-системы.
        Используется для формирования контекста (промпта) нейросети.
        """
        query = """
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'employees', 'departments', 'positions', 'employment_history', 
            'vacations', 'bonuses', 'trainings', 'employee_trainings', 
            'projects', 'project_assignments', 'performance_reviews', 'job_openings'
        )
        ORDER BY table_name, ordinal_position;
        """
        results, _ = self.execute_query(query)
        return results

# Создаем глобальный экземпляр для использования в приложении
db = Database()

def init_db():
    """Инициализация БД при запуске приложения"""
    if db.connect():
        try:
            # Проверка наличия таблиц в схеме
            tables_query = """
                SELECT count(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """
            result, _ = db.execute_query(tables_query)
            table_count = result[0][0]
            print(f"📊 В схеме 'public' обнаружено таблиц: {table_count}")
            return True
        except Exception as e:
            print(f"⚠️ Ошибка при проверке таблиц: {e}")
            return True # Все равно возвращаем True, если соединение есть
    return False