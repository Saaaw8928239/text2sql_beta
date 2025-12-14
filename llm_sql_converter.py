# llm_sql_converter.py - ИСПРАВЛЕННАЯ ВЕРСИЯ
import re
import torch

class LLMSQLConverter:
    def __init__(self, model_name="distilgpt2"):
        """
        Используем модель для Text-to-SQL
        """
        print(f"🔄 Загрузка модели {model_name}...")
        
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   Устройство: {self.device}")
        
        # Пробуем загрузить модель
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # ПРОСТАЯ загрузка без сложных параметров
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto" if self.device == "cuda" else None,
                local_files_only=True 
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            print("✅ Модель успешно загружена!")
            self.model_loaded = True
            
        except Exception as e:
            print(f"❌ Не удалось загрузить модель: {e}")
            print("   Использую улучшенный fallback")
            self.model_loaded = False
        
        # Контекст базы данных
        self.db_schema = """
        База данных "company_db", таблица "employees":
        
        Столбцы:
        - id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
        - first_name (VARCHAR(50), NOT NULL) - имя
        - last_name (VARCHAR(50), NOT NULL) - фамилия  
        - patronymic (VARCHAR(50)) - отчество
        - department (VARCHAR(100), NOT NULL) - отдел: 'IT', 'Маркетинг', 'Финансы', 'Продажи', 'HR', 'Логистика', 'Закупки', 'Руководство'
        - position (VARCHAR(100), NOT NULL) - должность
        - salary (DECIMAL(10,2)) - зарплата в рублях
        - hire_date (DATE) - дата приема
        - email (VARCHAR(100)) - email
        
        Важно: Для поиска по отделу используй department = 'Название_отдела'.
        Для зарплаты используй salary >, <, =.
        """
    
    def _fallback_sql(self, query):
        """УЛУЧШЕННЫЙ fallback - теперь понимает зарплату!"""
        import re
        query_lower = query.lower()
        
        # Извлекаем число
        numbers = re.findall(r'\d+', query)
        amount = numbers[0] if numbers else None
        
        # Определяем оператор
        operator = None
        if "больше" in query_lower or "выше" in query_lower or "свыше" in query_lower:
            operator = ">"
        elif "меньше" in query_lower or "ниже" in query_lower or "менее" in query_lower:
            operator = "<"
        elif "равно" in query_lower or "равен" in query_lower:
            operator = "="
        elif "от" in query_lower and "до" in query_lower:
            # Обработка диапазона "от X до Y"
            if numbers and len(numbers) >= 2:
                return f"SELECT first_name, last_name, position, department, salary FROM employees WHERE salary BETWEEN {numbers[0]} AND {numbers[1]};"
        
        # Основная логика
        base_select = "SELECT first_name, last_name, position, department, salary"
        
        if "все" in query_lower and "сотрудник" in query_lower:
            if amount and operator:
                # "всех сотрудников с зарплатой меньше 150000"
                return f"{base_select} FROM employees WHERE salary {operator} {amount};"
            else:
                return "SELECT * FROM employees;"
        
        elif "зарплат" in query_lower or "оклад" in query_lower or "доход" in query_lower:
            if amount and operator:
                return f"{base_select} FROM employees WHERE salary {operator} {amount};"
            elif "средн" in query_lower:
                return "SELECT AVG(salary) as avg_salary FROM employees;"
            else:
                return f"{base_select} FROM employees ORDER BY salary DESC LIMIT 10;"
        
        elif "ит" in query_lower or "it" in query_lower:
            if amount and operator and "зарплат" in query_lower:
                # "ит с зарплатой больше X"
                return f"{base_select} FROM employees WHERE department = 'IT' AND salary {operator} {amount};"
            else:
                return f"{base_select} FROM employees WHERE department = 'IT';"
        
        elif "менеджер" in query_lower:
            if amount and operator and "зарплат" in query_lower:
                return f"{base_select} FROM employees WHERE position ILIKE '%менеджер%' AND salary {operator} {amount};"
            else:
                return f"{base_select} FROM employees WHERE position ILIKE '%менеджер%';"
        
        elif "сортир" in query_lower or "упорядоч" in query_lower:
            if "зарплат" in query_lower:
                direction = "DESC" if "убыван" in query_lower else "ASC"
                return f"{base_select} FROM employees ORDER BY salary {direction};"
            elif "фамили" in query_lower:
                return f"{base_select} FROM employees ORDER BY last_name ASC;"
        
        elif "сколько" in query_lower or "количеств" in query_lower:
            if "ит" in query_lower:
                return "SELECT COUNT(*) as count FROM employees WHERE department = 'IT';"
            elif "менеджер" in query_lower:
                return "SELECT COUNT(*) as count FROM employees WHERE position ILIKE '%менеджер%';"
            else:
                return "SELECT COUNT(*) as count FROM employees;"
        
        # Если ничего не подошло - возвращаем ограниченный набор
        return "SELECT first_name, last_name, position, department, salary FROM employees LIMIT 10;"
    
    def generate_sql_with_llm(self, query):
        """Генерация SQL через настоящую LLM"""
        try:
            prompt = f"""
            Преобразуй запрос на русском в SQL.
            
            Схема БД: {self.db_schema}
            
            Запрос: {query}
            
            SQL (только запрос, без объяснений):
            """
            
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
            inputs = inputs.to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.1,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            sql = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Извлекаем SQL из ответа
            if "SQL" in sql:
                sql = sql.split("SQL")[-1].strip()
            
            # Очищаем
            sql = re.sub(r'```sql|```', '', sql).strip()
            if not sql.endswith(';'):
                sql += ';'
                
            return sql
            
        except Exception as e:
            print(f"   ⚠️  Ошибка LLM генерации: {e}")
            return None
    
    def convert(self, query):
        """Основной метод конвертации"""
        try:
            print(f"\n{'='*60}")
            print(f"🤖 Обработка: '{query}'")
            
            # Пробуем LLM если она загружена
            if self.model_loaded:
                print("   Использую LLM...")
                sql = self.generate_sql_with_llm(query)
                
                if sql and "SELECT" in sql.upper():
                    print(f"✅ LLM SQL: {sql}")
                    return {
                        'success': True,
                        'sql_query': sql,
                        'entities': {},
                        'lemmas': []
                    }
                else:
                    print("   LLM не сгенерировала SQL, переключаюсь на fallback")
            
            # Используем fallback
            print("   Использую улучшенный fallback")
            sql = self._fallback_sql(query)
            print(f"✅ Fallback SQL: {sql}")
            
            return {
                'success': True,
                'sql_query': sql,
                'entities': {},
                'lemmas': []
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'sql_query': None
            }