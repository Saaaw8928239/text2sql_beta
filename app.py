# app.py - ОБНОВЛЕННАЯ ВЕРСИЯ ДЛЯ СХЕМЫ ИЗ 12 ТАБЛИЦ
from flask import Flask, render_template, request, jsonify
from llm_sql_converter import LLMSQLConverter
from database import db, init_db
import json
import os
from datetime import datetime

app = Flask(__name__)

# Инициализация LLM-конвертера
print("🚀 Инициализация Text2SQL системы с Qwen 2.5...")
converter = LLMSQLConverter()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ИСТОРИЕЙ =====
HISTORY_FILE = 'query_history.json'

def load_history():
    """Загрузка истории запросов из файла"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history if isinstance(history, list) else []
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")
            return []
    return []

def save_history(history):
    """Сохранение истории запросов в файл"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

# Загружаем историю при старте
query_history = load_history()

# ===== МАРШРУТЫ (ROUTES) =====

@app.route('/')
def index():
    return render_template('index.html', title="Text2SQL HR System", query_history=query_history[:10])

@app.route('/api/query', methods=['POST'])
def process_query():
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'success': False, 'error': 'Пустой запрос'})

    start_time = datetime.now()
    
    # 1. Конвертация текста в SQL через LLM
    conversion_result = converter.convert(user_query)
    
    if not conversion_result['success']:
        return jsonify(conversion_result)
    
    sql_query = conversion_result['sql_query']
    
    # 2. Выполнение SQL в базе данных
    try:
        results, columns = db.execute_query(sql_query)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Обновляем историю
        if user_query not in query_history:
            query_history.insert(0, user_query)
            save_history(query_history)
        
        return jsonify({
            'success': True,
            'sql_query': sql_query,
            'columns': columns,
            'data': results,
            'execution_time': f"{execution_time:.2f} сек.",
            'row_count': len(results) if results else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Ошибка выполнения SQL: {str(e)}",
            'sql_query': sql_query
        })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    global query_history
    query_history = []
    save_history(query_history)
    return jsonify({'success': True, 'history': []})

@app.route('/api/db_info')
def get_db_info():
    """Получение статистики по новой структуре БД"""
    try:
        # Считаем данные по ключевым таблицам
        emp_count, _ = db.execute_query("SELECT COUNT(*) FROM employees;")
        dep_count, _ = db.execute_query("SELECT COUNT(*) FROM departments;")
        proj_count, _ = db.execute_query("SELECT COUNT(*) FROM projects;")
        
        return jsonify({
            'success': True,
            'stats': {
                'employees': emp_count[0][0],
                'departments': dep_count[0][0],
                'projects': proj_count[0][0]
            }
        })
    except:
        return jsonify({'success': False})

# ===== ЗАПУСК ПРИЛОЖЕНИЯ =====

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 ЗАПУСК ДИПЛОМНОГО ПРОЕКТА: NL2SQL HR SYSTEM")
    print("="*80)
    
    print(f"🤖 Модель: Qwen 2.5 (3B Instruct)")
    print(f"📊 Таблиц в схеме: 12")
    
    # Инициализация БД
    if init_db():
        print("✅ База данных подключена успешно")
        
        try:
            # Проверочный запрос с JOIN для новой структуры
            test_query = """
                SELECT e.first_name, e.last_name, d.department_name 
                FROM employees e
                LEFT JOIN departments d ON e.department_id = d.id 
                LIMIT 3;
            """
            results, columns = db.execute_query(test_query)
            print(f"📋 Пример данных (Сотрудник + Отдел):")
            for row in results:
                dep = row[2] if row[2] else "Нет отдела"
                print(f"   - {row[0]} {row[1]} | {dep}")
        except Exception as e:
            print(f"⚠️ Ошибка проверки данных: {e}")
    else:
        print("❌ Критическая ошибка: Не удалось подключиться к PostgreSQL")

    app.run(debug=False, port=5000)