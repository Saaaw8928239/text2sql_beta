import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

class LLMSQLConverter:
    def __init__(self, model_name="Qwen/Qwen2.5-3B-Instruct"):
        print(f"🔄 Загрузка модели {model_name} для новой схемы БД...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False

        # Описание схемы на русском, чтобы модель лучше сопоставляла понятия
        self.database_schema = """
        Таблицы и колонки в PostgreSQL:
        1. employees (Сотрудники): id, first_name (имя), last_name (фамилия), patronymic (отчество), birth_date, gender (пол: 'Мужской', 'Женский'), email, phone, hire_date, termination_date, is_active, department_id, position_id, manager_id, salary (оклад), bonus_percent
        2. departments (Отделы): id, department_name (название отдела), department_code, head_of_department_id, budget, location, phone, parent_department_id
        3. positions (Должности): id, position_name (название), position_level (Junior, Middle, Senior, Lead, Head), category, min_salary, max_salary, required_experience_years
        4. employment_history: id, employee_id, position_id, department_id, salary, start_date, end_date, change_reason
        5. vacations (Отпуска): id, employee_id, vacation_type, start_date, end_date, status, approved_by
        6. bonuses (Премии): id, employee_id, bonus_amount, bonus_date, bonus_reason, quarter (квартал), year (год)
        7. trainings (Обучение): id, training_name, training_type, start_date, end_date, cost, provider
        8. employee_trainings: id, employee_id, training_id, completion_date, grade, certificate_received
        9. projects (Проекты): id, project_name, project_manager_id, department_id, start_date, end_date, status, budget
        10. project_assignments: id, employee_id, project_id, role, hours_allocated, assignment_date, completion_percentage
        11. performance_reviews: id, employee_id, reviewer_id, review_date, rating, comments, goals
        12. job_openings (Вакансии): id, position_id, department_id, opening_date, status, salary_range_min, salary_range_max

        Важные связи:
        - employees.department_id = departments.id
        - employees.position_id = positions.id
        - vacations.employee_id = employees.id
        - bonuses.employee_id = employees.id
        - project_assignments.employee_id = employees.id
        """

        try:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
            )
            self.model_loaded = True
            print(f"✅ Модель загружена. VRAM: {self.model.get_memory_footprint() / 1024**3:.2f} GB")

        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")

    def generate_sql_with_llm(self, user_query):
        """Генерация SQL на основе русского промпта"""
        if not self.model_loaded:
            return None

        # Промпт полностью на русском для лучшего понимания кириллицы
        prompt = f"""Ты — эксперт по SQL. Твоя задача: перевести запрос пользователя на естественном языке в корректный SQL-запрос для PostgreSQL.

        СХЕМА БАЗЫ ДАННЫХ:
        {self.database_schema}

        ПРАВИЛА:
        1. Используй только указанные таблицы и колонки.
        2. Для текстового поиска используй оператор ILIKE (например, department_name ILIKE '%IT%').
        3. Если нужно название отдела или должности, обязательно делай JOIN с соответствующей таблицей.
        4. Если в запросе есть упоминание имен, фамилий или названий на русском, используй их в SQL.
        5. Ответ должен содержать ТОЛЬКО чистый SQL-запрос, без пояснений и без кавычек.

        ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_query}
        SQL:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=300, 
                temperature=0.1, 
                top_p=0.9
            )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Извлекаем часть после "SQL:"
        if "SQL:" in full_response:
            sql = full_response.split("SQL:")[-1].strip()
        else:
            sql = full_response.strip()

        # Очистка от мусора
        sql = sql.replace("```sql", "").replace("```", "").strip()
        sql = sql.split(';')[0] + ';' # Оставляем только первый запрос до точки с запятой
            
        return sql

    def convert(self, query):
        """Интерфейс для app.py"""
        try:
            print(f"\n🤖 Обработка запроса: '{query}'")
            
            if self.model_loaded:
                sql = self.generate_sql_with_llm(query)
                
                if sql and "SELECT" in sql.upper():
                    print(f"✅ Сгенерирован SQL: {sql}")
                    return {
                        'success': True,
                        'sql_query': sql,
                        'entities': {},
                        'lemmas': []
                    }
            
            return {'success': False, 'error': "Не удалось создать SQL"}
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {'success': False, 'error': str(e)}