from flask import Flask, render_template, request, jsonify, send_file, make_response
from llm_sql_converter import LLMSQLConverter
from database import db, init_db
import json
import os
import re
from datetime import datetime
from decimal import Decimal
from fpdf import FPDF
import io

app = Flask(__name__)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app.json_encoder = DecimalEncoder

print("Инициализация Text2SQL системы с Qwen 2.5...")
converter = LLMSQLConverter()

HISTORY_FILE = 'query_history.json'

def load_history():
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
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

query_history = load_history()
if not os.path.exists(HISTORY_FILE):
    save_history([])
    print("Создан новый файл истории запросов")

def convert_decimal_in_results(results):
    if not results:
        return results
    converted = []
    for row in results:
        if isinstance(row, (list, tuple)):
            new_row = []
            for value in row:
                if isinstance(value, Decimal):
                    new_row.append(float(value))
                else:
                    new_row.append(value)
            converted.append(tuple(new_row) if isinstance(row, tuple) else new_row)
        else:
            converted.append(row)
    return converted

# ЗАЩИТА ОТ SQL-ИНЪЕКЦИЙ И ОПАСНЫХ ЗАПРОСОВ
DANGEROUS_SQL_KEYWORDS = [
    'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER',
    'CREATE', 'REPLACE', 'GRANT', 'REVOKE', 'EXECUTE', 'EXEC',
]

DANGEROUS_NL_PATTERNS = [
    r'\bудал[иьяешьте]+\b', r'\bстер[иьёт]+\b', r'\bочист[иьь]+\b',
    r'\bсброс\w*\b', r'\bизмен[иьяешьте]+\b', r'\bобнов[иьляешьте]+\b',
    r'\bредактир\w+\b', r'\bдобав[иьляешьте]+\b', r'\bвстав[иьляешьте]+\b',
    r'\bсозда[тьёюй]\b', r'\bсоздай\b',
    r'\bdrop\b', r'\bdelete\b', r'\btruncate\b', r'\bupdate\b', r'\binsert\b',
]

def check_nl_safety(user_query: str):
    lower_query = user_query.lower()
    for pattern in DANGEROUS_NL_PATTERNS:
        if re.search(pattern, lower_query):
            return False, (
                "Операции изменения или удаления данных недоступны.\n"
                "Система работает только в режиме чтения. "
                "Задайте вопрос для получения информации из базы данных."
            )
    return True, ""

def check_sql_safety(sql: str):
    stripped = sql.strip().upper()
    if not (stripped.startswith('SELECT') or stripped.startswith('WITH')):
        return False, "Разрешены только SELECT-запросы. Изменение и удаление данных недоступно."
    for kw in DANGEROUS_SQL_KEYWORDS:
        if re.search(r'\b' + kw + r'\b', stripped):
            return False, f"Запрос содержит запрещённую операцию ({kw}). Изменять или удалять данные нельзя."
    if re.search(r';\s*\w', sql):
        return False, "Обнаружена попытка выполнения нескольких запросов. Разрешён только один SELECT."
    return True, ""

# УТОЧНЯЮЩИЙ ДИАЛОГ
def get_clarification_suggestions():
    return [
        "Покажи всех сотрудников с зарплатой выше 100 000 ₽",
        "Сколько сотрудников в каждом отделе?",
        "Топ 5 сотрудников по зарплате",
        "Показать активные проекты",
        "Средняя зарплата по должностям",
    ]

# ЭКСПОРТ В PDF
@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    try:
        req_data = request.json
        data = req_data.get('data', [])
        
        if not data:
            return jsonify({'success': False, 'error': 'Нет данных для экспорта'}), 400

        # Инициализация FPDF
        pdf = FPDF()
        pdf.add_page()
        
        font_path = os.path.join(os.path.dirname(__file__), 'times.ttf')
        
        if os.path.exists(font_path):
            # Регистрируем шрифт под именем 'TimesNewRoman'
            pdf.add_font('TimesNewRoman', '', font_path, uni=True)
            pdf.set_font('TimesNewRoman', size=12)
        else:
            # Если файл не найден, используем стандартный Helvetica
            pdf.set_font('helvetica', size=12)
            print(f"Шрифт {font_path} не найден! Используется стандартный.")

        headers = list(data[0].keys())
        col_width = 190 / len(headers)
        
        pdf.set_fill_color(200, 220, 255)
        for header in headers:
            pdf.cell(col_width, 10, str(header), border=1, fill=True)
        pdf.ln()

        # Данные
        pdf.set_fill_color(255, 255, 255)
        for row in data:
            for header in headers:
                val = str(row[header]) if row[header] is not None else "-"
                pdf.cell(col_width, 10, val, border=1)
            pdf.ln()

        pdf_bytes = pdf.output()
        pdf_stream = io.BytesIO(pdf_bytes)
        
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='report.pdf'
        )
        
    except Exception as e:
        print(f"Ошибка при создании PDF: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# МАРШРУТЫ
@app.route('/')
def index():
    return render_template('index.html', title="Text2SQL HR System", query_history=query_history[:10])

@app.route('/api/query', methods=['POST'])
def process_query():
    global query_history
    data = request.json
    user_query = data.get('query', '').strip()

    if not user_query:
        return jsonify({'success': False, 'error': 'Пустой запрос'})

    # Безопасность запроса на естественном языке
    nl_safe, nl_reason = check_nl_safety(user_query)
    if not nl_safe:
        return jsonify({'success': False, 'blocked': True, 'error': nl_reason})

    start_time = datetime.now()

    # LLM конвертация
    conversion_result = converter.convert(user_query)
    if not conversion_result['success']:
        return jsonify(conversion_result)

    sql_query = conversion_result['sql_query']
    understood = conversion_result.get('understood', True)

    # Если LLM сказала "НЕ ПОНЯЛ"
    if not understood:
        return jsonify({
            'success': False,
            'needs_clarification': True,
            'message': f'Не удалось понять запрос «{user_query}». Попробуйте переформулировать.',
            'suggestions': get_clarification_suggestions(),
            'sql_query': sql_query
        })

    # Безопасность SQL
    sql_safe, sql_reason = check_sql_safety(sql_query)
    if not sql_safe:
        return jsonify({'success': False, 'blocked': True, 'error': f' {sql_reason}', 'sql_query': sql_query})

    # Выполнение
    try:
        results, columns = db.execute_query(sql_query)
        serializable_results = convert_decimal_in_results(results)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Преобразуем результаты в список словарей для удобного экспорта
        formatted_results = []
        if results and columns:
            for row in results:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i] if i < len(row) else None
                formatted_results.append(row_dict)

        if user_query not in query_history:
            query_history.insert(0, user_query)
            save_history(query_history[:50])

        return jsonify({
            'success': True,
            'sql_query': sql_query,
            'columns': columns,
            'data': serializable_results,
            'formatted_data': formatted_results,  
            'execution_time': f"{execution_time:.2f} сек.",
            'row_count': len(results) if results else 0,
            'history': query_history[:10]
        })

    except Exception as e:
        print(f"Ошибка выполнения SQL: {e}")
        return jsonify({'success': False, 'error': f"Ошибка выполнения SQL: {str(e)}", 'sql_query': sql_query})

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    global query_history
    query_history = []
    save_history(query_history)
    return jsonify({'success': True, 'history': []})

@app.route('/api/sample_queries', methods=['GET'])
def get_sample_queries():
    samples = [
        "Покажи топ 5 сотрудников с самой высокой зарплатой",
        "Сколько сотрудников в каждом отделе?",
        "Найти всех разработчиков с зарплатой больше 150000",
        "Показать активные проекты и их бюджеты",
        "Средняя зарплата по должностям",
        "Кто из сотрудников был в отпуске в июле 2024?"
    ]
    return jsonify({'samples': samples})

@app.route('/api/db_info')
def get_db_info():
    try:
        emp_count, _ = db.execute_query("SELECT COUNT(*) FROM employees;")
        dep_count, _ = db.execute_query("SELECT COUNT(*) FROM departments;")
        proj_count, _ = db.execute_query("SELECT COUNT(*) FROM projects;")
        return jsonify({
            'success': True,
            'stats': {
                'employees': emp_count[0][0] if emp_count else 0,
                'departments': dep_count[0][0] if dep_count else 0,
                'projects': proj_count[0][0] if proj_count else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("\n" + "="*80)
    print("ЗАПУСК ДИПЛОМНОГО ПРОЕКТА: NL2SQL HR SYSTEM")
    print("="*80)
    if init_db():
        print("База данных подключена успешно")
    else:
        print("Критическая ошибка: Не удалось подключиться к PostgreSQL")
    print("🌐 Запуск сервера на http://localhost:5000")
    app.run(debug=False, port=5000)