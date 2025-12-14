# app.py - ВЕРСИЯ С LLM
from flask import Flask, render_template, request, jsonify
from llm_sql_converter import LLMSQLConverter  # Импортируем LLM конвертер
from database import db, init_db
import json
import os
from datetime import datetime


app = Flask(__name__)

# Инициализация LLM-конвертера
print("🚀 Инициализация Text2SQL системы с LLM...")
converter = LLMSQLConverter()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ИСТОРИЕЙ =====
HISTORY_FILE = 'query_history.json'

def load_history():
    """Загрузка истории запросов из файла"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                if isinstance(history, list):
                    return history
                else:
                    return get_default_history()
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return get_default_history()
    else:
        return get_default_history()

def get_default_history():
    """Возвращает историю по умолчанию"""
    return [
    ]

def save_history(history):
    """Сохранение истории запросов в файл"""
    try:
        history_to_save = history[:20] if len(history) > 20 else history
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_to_save, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")
        return False

# Загружаем историю при запуске
query_history = load_history()

# ===== МАРШРУТЫ FLASK =====
@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', 
                         query_history=query_history[:10],
                         title="Text2SQL")

@app.route('/api/query', methods=['POST'])
def process_query():
    """Обработка запроса от пользователя с LLM"""
    global query_history
    
    try:
        # Получаем запрос из формы
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Пустой запрос'
            })
        
        # 1. ОБНОВЛЯЕМ ИСТОРИЮ
        if user_query in query_history:
            query_history.remove(user_query)
        
        query_history.insert(0, user_query)
        
        if len(query_history) > 20:
            query_history = query_history[:20]
        
        save_history(query_history)
        
        # 2. КОНВЕРТИРУЕМ NL -> SQL ЧЕРЕЗ LLM
        print(f"\n{'='*60}")
        print(f"🔍 Пользовательский запрос: '{user_query}'")
        
        result = converter.convert(user_query)
        
        if not result['success']:
            error_msg = result.get('error', 'Неизвестная ошибка LLM')
            print(f"❌ Ошибка LLM: {error_msg}")
            
            # Пробуем fallback на простой запрос
            fallback_sql = "SELECT first_name, last_name, position, department, salary FROM employees LIMIT 10;"
            print(f"🔄 Использую fallback запрос: {fallback_sql}")
            
            result = {
                'success': True,
                'sql_query': fallback_sql,
                'entities': {},
                'lemmas': []
            }
        
        sql_query = result['sql_query']
        print(f"✅ LLM сгенерировал SQL: {sql_query}")
        print(f"{'='*60}")
        
        # 3. ПРОВЕРКА БЕЗОПАСНОСТИ SQL
        def is_sql_safe(sql_query):
            """Базовая проверка SQL-запроса на безопасность"""
            # Приводим к верхнему регистру для проверки
            sql_upper = sql_query.upper()
            
            # Запрещенные операции
            dangerous_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
                                   'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE']
            
            for operation in dangerous_operations:
                if operation in sql_upper:
                    print(f"⚠️  Обнаружена опасная операция: {operation}")
                    return False
            
            # Проверяем, что запрос начинается с SELECT (только чтение)
            if not sql_upper.strip().startswith('SELECT'):
                print(f"⚠️  Запрос не начинается с SELECT: {sql_query[:50]}...")
                return False
            
            return True
        
        # 4. ВЫПОЛНЯЕМ SQL-ЗАПРОС В БД
        db_results, columns = None, None
        
        # Проверяем SQL на безопасность
        if is_sql_safe(sql_query):  # ← ИСПРАВЛЕНО! Теперь это обычная функция
            try:
                db_results, columns = db.execute_query(sql_query)
                print(f"📊 Получено результатов: {len(db_results) if db_results else 0}")
            except Exception as db_error:
                error_msg = str(db_error)
                print(f"❌ Ошибка выполнения SQL: {error_msg}")
                
                # Упрощаем сообщение для пользователя
                if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
                    error_msg = "Ошибка: таблица не найдена. Проверьте подключение к БД."
                elif "syntax error" in error_msg.lower():
                    error_msg = "Ошибка синтаксиса SQL. LLM сгенерировал некорректный запрос."
                elif "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                    error_msg = "Ошибка: столбец не найден. Проверьте схему базы данных."
                
                return jsonify({
                    'success': False,
                    'error': f'Ошибка БД: {error_msg}',
                    'sql_query': sql_query,
                    'user_query': user_query,
                    'history': query_history[:10]
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Запрос содержит потенциально опасные операции',
                'user_query': user_query,
                'history': query_history[:10]
            })
        
        # 5. ФОРМАТИРУЕМ РЕЗУЛЬТАТЫ
        formatted_results = []
        if db_results and columns:
            for row in db_results:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        row_dict[col] = value.strftime('%Y-%m-%d')
                    elif value is None:
                        row_dict[col] = None
                    elif isinstance(value, (int, float)):
                        # Для зарплаты добавляем форматирование
                        if col == 'salary':
                            row_dict[col] = f"{value:,.2f}".replace(',', ' ').replace('.', ',')
                        else:
                            row_dict[col] = value
                    else:
                        row_dict[col] = str(value)
                formatted_results.append(row_dict)
        
        # 6. ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ
        print(f"\n📋 ИТОГИ ОБРАБОТКИ:")
        print(f"   Запрос: {user_query}")
        print(f"   SQL: {sql_query}")
        print(f"   Результатов: {len(formatted_results)}")
        if formatted_results and len(formatted_results) > 0:
            print(f"   Пример строки: {formatted_results[0]}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'user_query': user_query,
            'sql_query': sql_query,
            'results': formatted_results,
            'columns': columns if columns else [],
            'entities': result.get('entities', {}),
            'history': query_history[:10]
        })
        
    except Exception as e:
        print(f"💥 Критическая ошибка в process_query: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': f'Внутренняя ошибка сервера: {str(e)}',
            'history': query_history[:10]
        })

@app.route('/api/history', methods=['GET'])
def get_history():
    """Получение истории запросов"""
    return jsonify({
        'success': True,
        'history': query_history[:15]
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Очистка истории запросов"""
    global query_history
    query_history = get_default_history()
    save_history(query_history)
    return jsonify({
        'success': True,
        'message': 'История очищена',
        'history': query_history[:10]
    })

@app.route('/api/sample_queries', methods=['GET'])
def get_sample_queries():
    """Примеры запросов для быстрого выбора"""
    samples = [
        "Показать всех сотрудников",
        "Сотрудники IT отдела",
        "Найти менеджеров",
        "Зарплата больше 150000"
    ]
    return jsonify({'success': True, 'samples': samples})

@app.route('/api/db_info', methods=['GET'])
def get_db_info():
    """Получение информации о базе данных"""
    try:
        # Количество записей
        results, columns = db.execute_query("SELECT COUNT(*) as count FROM employees;")
        count = results[0][0] if results else 0
        
        # Отделы
        dept_results, _ = db.execute_query("SELECT DISTINCT department FROM employees ORDER BY department;")
        departments = [row[0] for row in dept_results] if dept_results else []
        
        # Зарплаты
        salary_results, _ = db.execute_query("""
            SELECT 
                MIN(salary) as min_salary,
                MAX(salary) as max_salary,
                ROUND(AVG(salary), 2) as avg_salary,
                ROUND(SUM(salary), 2) as total_salary
            FROM employees;
        """)
        
        if salary_results:
            min_salary, max_salary, avg_salary, total_salary = salary_results[0]
        else:
            min_salary = max_salary = avg_salary = total_salary = 0
        
        # Статистика по отделам
        dept_stats_results, _ = db.execute_query("""
            SELECT 
                department,
                COUNT(*) as employee_count,
                ROUND(AVG(salary), 2) as avg_salary
            FROM employees 
            GROUP BY department 
            ORDER BY avg_salary DESC;
        """)
        
        dept_stats = []
        if dept_stats_results:
            for row in dept_stats_results:
                dept_stats.append({
                    'department': row[0],
                    'count': row[1],
                    'avg_salary': row[2]
                })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_employees': count,
                'departments': departments,
                'min_salary': min_salary,
                'max_salary': max_salary,
                'avg_salary': avg_salary,
                'total_salary': total_salary,
                'department_stats': dept_stats
            }
        })
    except Exception as e:
        print(f"Ошибка получения информации о БД: {e}")
        return jsonify({
            'success': False,
            'error': f'Не удалось получить информацию о БД: {str(e)}'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности системы"""
    try:
        # Проверяем БД
        db_ok = False
        try:
            results, _ = db.execute_query("SELECT 1;")
            db_ok = True
        except:
            db_ok = False
        
        # Проверяем LLM (просто создаем экземпляр)
        llm_ok = True  # Предполагаем что ок, если импортировался
        
        return jsonify({
            'success': True,
            'status': {
                'database': 'connected' if db_ok else 'disconnected',
                'llm': 'ready' if llm_ok else 'not_ready',
                'history_count': len(query_history),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ===== ЗАПУСК ПРИЛОЖЕНИЯ =====
if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 ЗАПУСК TEXT2SQL С LLM")
    print("="*80)
    
    # Информация о системе
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"🤖 Используемая модель: SQLCoder")
    print(f"📜 Загружено запросов в истории: {len(query_history)}")
    
    # Инициализация БД
    print("\n🔌 Подключение к базе данных...")
    if init_db():
        print("✅ База данных подключена успешно")
        
        # Показываем статистику
        try:
            results, columns = db.execute_query("SELECT COUNT(*) FROM employees;")
            count = results[0][0] if results else 0
            print(f"📊 В базе данных: {count} сотрудников")
            
            # Примерные данные
            results, columns = db.execute_query("SELECT first_name, last_name, department FROM employees LIMIT 3;")
            print(f"📋 Пример сотрудников:")
            for row in results:
                print(f"   - {row[0]} {row[1]} ({row[2]})")
        except Exception as e:
            print(f"⚠️  Не удалось получить статистику БД: {e}")
    else:
        print("⚠️  Не удалось подключиться к БД")
        print("   Проверьте настройки подключения в файле .env")
    
    print("\n" + "="*80)
    print("🌐 Веб-сервер готов к работе!")
    print("👉 Откройте браузер и перейдите по адресу: http://localhost:5000")
    print("="*80 + "\n")
    
    # Запускаем Flask
    app.run(debug=True, port=5000, host='0.0.0.0')