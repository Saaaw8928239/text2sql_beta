import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

class LLMSQLConverter:
    def __init__(self, model_name="Qwen/Qwen2.5-3B-Instruct"):
        print(f"Загрузка модели {model_name} для 12 таблиц БД...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_loaded = False
        
        self.cache = {}

        # ПОЛНАЯ СХЕМА БД (12 таблиц)
        self.database_schema = """
        ВАЖНО: Используй ТОЛЬКО эти таблицы и колонки. Не выдумывай новые!

        ТАБЛИЦЫ PostgreSQL:
        1. employees (сотрудники):
           - id, first_name, last_name, patronymic, birth_date
           - gender ('Мужской', 'Женский')
           - email, phone
           - salary (число)
           - department_id (связь с departments.id)
           - position_id (связь с positions.id)
           - manager_id (связь с employees.id - кто руководитель)
           - is_active (boolean), hire_date, termination_date

        2. departments (отделы):
           - id, department_name, department_code
           - head_of_department_id (связь с employees.id)

        3. positions (должности):
           - id, position_name, position_level, category
           - min_salary, max_salary

        4. employment_history (история трудоустройства):
           - id, employee_id, position_id, department_id, salary
           - start_date, end_date, change_reason

        5. vacations (отпуска):
           - id, employee_id, vacation_type ('Annual','Sick','Unpaid','Educational')
           - start_date, end_date, status ('Approved','Pending','Rejected')

        6. bonuses (премии):
           - id, employee_id, bonus_amount, bonus_date, bonus_reason
           - quarter, year

        7. trainings (обучения):
           - id, training_name, training_type, cost

        8. employee_trainings (связь сотрудников с обучением):
           - id, employee_id, training_id, completion_date, grade

        9. projects (проекты):
           - id, project_name, status ('Planning','Active','Completed','OnHold','Cancelled')
           - budget, project_manager_id, department_id, start_date

        10. project_assignments (участие в проектах):
            - id, employee_id, project_id, role, hours_allocated

        11. performance_reviews (оценки):
            - id, employee_id, rating (1-5), comments, review_date

        12. job_openings (вакансии):
            - id, position_id, department_id, status ('Open','Closed','OnHold')
            - opening_date, closing_date, salary_range_min, salary_range_max

        СВЯЗИ (JOIN):
        - employees.department_id = departments.id
        - employees.position_id = positions.id
        - employees.manager_id = employees.id (самосвязь для руководителей)
        - departments.head_of_department_id = employees.id
        - vacations.employee_id = employees.id
        - bonuses.employee_id = employees.id
        - project_assignments.employee_id = employees.id
        - project_assignments.project_id = projects.id
        - employee_trainings.employee_id = employees.id
        - employee_trainings.training_id = trainings.id
        - performance_reviews.employee_id = employees.id
        - job_openings.position_id = positions.id
        - job_openings.department_id = departments.id
        - employment_history.employee_id = employees.id
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
            print(f"Модель готова. VRAM: {self.model.get_memory_footprint() / 1024**3:.2f} GB")

        except Exception as e:
            print(f"Ошибка загрузки: {e}")

    def generate_sql_with_llm(self, user_query):
        if not self.model_loaded:
            return "SELECT 1 as result;", False

        prompt = f"""<|im_start|>system
Ты — эксперт по PostgreSQL и аналитике кадровых данных. 
Твоя задача: перевести вопрос пользователя в ОДИН точный SQL запрос.
1. ЕСЛИ запрос можно перевести в SQL — напиши SQL и на новой строке "ПОНЯЛ".
2. ЕСЛИ запрос не относится к БД (приветствие, бессмыслица, погода) — напиши "SELECT 1 as result;" и на новой строке "НЕ ПОНЯЛ".

СТРОГИЕ ПРАВИЛА:
1. Используй только PostgreSQL синтаксис.
2. Для поиска по тексту всегда используй ILIKE (например, name ILIKE '%иван%').
3. Работа с датами: вместо YEAR(d) используй EXTRACT(YEAR FROM d). Вместо MONTH(d) используй EXTRACT(MONTH FROM d).
4. Связи: Если вопрос требует данных из нескольких таблиц, всегда используй JOIN по внешним ключам (id).
5. Агрегация: Используй COUNT(*), SUM(salary), AVG(salary) с соответствующим GROUP BY.
6. Выводи только чистый SQL. В конце, с новой строки, напиши вердикт "ПОНЯЛ" или "НЕ ПОНЯЛ".
7. Используй только колонки и таблицы, которые тебе даны, не выдумывай новых названий.
8. Таблицы и колонки (ТОЛЬКО ЭТИ, НЕ ВЫДУМЫВАЙ НОВЫЕ):
   - employees: id, first_name, last_name, phone (а НЕ phone_number!), salary, department_id, position_id, manager_id, is_active, hire_date, termination_date
   - departments: id, department_name, head_of_department_id
   - positions: id, position_name
   - vacations: id, employee_id, start_date, end_date
   - bonuses: id, employee_id, bonus_amount, bonus_date
   - projects: id, project_name, status, budget
   - job_openings: id, status (Open/Closed) — ЭТО ТАБЛИЦА ДЛЯ ВАКАНСИЙ, НЕ vacancies!

Примеры (Few-Shot):
Запрос: "Кто был в отпуске в 2024 году"
SQL: SELECT e.first_name, e.last_name FROM employees e JOIN vacations v ON e.id = v.employee_id WHERE EXTRACT(YEAR FROM v.start_date) = 2024;
ПОНЯЛ

Запрос: "-=-=-++"
SQL: SELECT 1 as result;
НЕ ПОНЯЛ

Вопрос: "Покажи всех сотрудников"
SQL: SELECT * FROM employees;
ПОНЯЛ

Вопрос: "Найти сотрудника с фамилией Волков"
SQL: SELECT * FROM employees WHERE last_name ILIKE '%волков%';
ПОНЯЛ

Вопрос: "Показать сотрудника с телефоном +7(916)111-11-11"
SQL: SELECT * FROM employees WHERE phone = '+7(916)111-11-11';
ПОНЯЛ

Вопрос: "Сколько сотрудников в каждом отделе"
SQL: SELECT d.department_name, COUNT(e.id) FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.department_name;
ПОНЯЛ

Вопрос: "Кто руководит отделом разработки"
SQL: SELECT e.first_name, e.last_name FROM employees e JOIN departments d ON e.id = d.head_of_department_id WHERE d.department_name ILIKE '%разработк%';
ПОНЯЛ

Вопрос: "Какие есть вакансии"
SQL: SELECT * FROM job_openings WHERE status = 'Open';
ПОНЯЛ

Вопрос: "Средняя зарплата по отделам"
SQL: SELECT d.department_name, AVG(e.salary) FROM employees e JOIN departments d ON e.department_id = d.id GROUP BY d.department_name;
ПОНЯЛ

Вопрос: "Привет"
SQL: SELECT 1 as result;
НЕ ПОНЯЛ

Схема БД:
{self.database_schema}
<|im_end|>
<|im_start|>user
Вопрос: {user_query}
<|im_end|>
<|im_start|>assistant"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=500, 
                temperature=0.01,
                repetition_penalty=1.1
            )
        
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_text.split("assistant")[-1].strip()

        
        sql_pattern = re.compile(r'(SELECT|WITH)[\s\S]+?(?=\s*ПОНЯЛ|\s*НЕ ПОНЯЛ|$)', re.IGNORECASE)
        sql_match = sql_pattern.search(response)
        
        if sql_match:
            sql_part = sql_match.group(0).strip()
            sql_part = sql_part.replace('```sql', '').replace('```', '').strip()
            if not sql_part.endswith(';'):
                sql_part += ";"
        else:
            sql_part = "SELECT 1 as result;"

        # Определение статуса "Понял"
        upper_resp = response.upper()
        if "НЕ ПОНЯЛ" in upper_resp:
            understood = False
        elif "ПОНЯЛ" in upper_resp and sql_part != "SELECT 1 as result;":
            understood = True
        else:
            # Если модель не выдала ключевое слово, но выдала похожий на правду SQL
            understood = sql_part.count(" ") > 2 

        return sql_part, understood

    def convert(self, query):
        try:
            query_norm = query.strip().lower()
            
            # Проверка кэша
            if query_norm in self.cache:
                print(f"Запрос из кэша: '{query}'")
                return self.cache[query_norm]

            # Логирование начала обработки
            print(f"Обработка: '{query}'")
            
            # Вызов генерации SQL
            sql, understood = self.generate_sql_with_llm(query)
            
            print(f"Итоговый SQL для БД: {sql}")
            print(f"Статус (Понял/Не понял): {'ПОНЯЛ' if understood else 'НЕ ПОНЯЛ'}")
            print("-" * 50)
            
            # Формирование результата
            result = {
                'success': True, 
                'sql_query': sql, 
                'understood': understood
            }
            
            # Кэшируем только успешно понятые запросы
            if understood:
                self.cache[query_norm] = result

            return result

        except Exception as e:
            # Обработка ошибок
            print(f"Критическая ошибка в convert: {e}")
            return {'success': False, 'error': str(e)}