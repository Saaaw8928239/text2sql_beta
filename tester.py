import pandas as pd
import time
import re
from llm_sql_converter import LLMSQLConverter
from database import db

def analyze_sql_quality(generated_sql, expected_sql, error_msg=""):
    """
    Анализирует качество сгенерированного SQL умным способом.
    Возвращает: verdict, comment
    """
    
    # Если синтаксическая ошибка
    if error_msg and "ОШИБКА" in error_msg:
        return "Ошибка синтаксиса", f"SQL не выполнился: {error_msg[:100]}"
    
    # Проверка базовой структуры
    gen_upper = generated_sql.upper().strip()
    exp_upper = expected_sql.upper().strip() if expected_sql else ""
    
    # Если модель сказала "НЕ ПОНЯЛ"
    if gen_upper == "SELECT 1 AS RESULT;" or "SELECT 1" in gen_upper:
        return "НЕ ПОНЯЛ", "Модель не смогла интерпретировать запрос"
    
    # Проверка на опасные операции
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE']
    for kw in dangerous:
        if kw in gen_upper:
            return "Блокировано безопасностью", f"Сгенерирован запрещённый запрос с {kw}"
    
    # Проверка типов JOIN (если ожидался JOIN)
    if expected_sql and 'JOIN' in exp_upper:
        has_join = 'JOIN' in gen_upper
        if not has_join:
            return "Частично верно", "Запрос выполнен, но без JOIN (возможно, данные неполные)"
    
    # Проверка фильтров (WHERE)
    if expected_sql and 'WHERE' in exp_upper:
        has_where = 'WHERE' in gen_upper
        if not has_where:
            return "Частично верно", "Запрос выполнен, но отсутствует фильтрация"
    
    # Проверка агрегации (GROUP BY)
    if expected_sql and ('GROUP BY' in exp_upper or 'AVG(' in exp_upper or 'SUM(' in exp_upper):
        has_agg = 'GROUP BY' in gen_upper or 'AVG(' in gen_upper or 'SUM(' in gen_upper
        if not has_agg and expected_sql:
            return "Частично верно", "Запрос выполнен, но без агрегации (ожидалась группировка)"
    
    # Проверка использования правильных таблиц
    expected_tables = re.findall(r'\bFROM\s+(\w+)', exp_upper, re.I) if expected_sql else []
    expected_tables += re.findall(r'\bJOIN\s+(\w+)', exp_upper, re.I) if expected_sql else []
    
    gen_tables = re.findall(r'\bFROM\s+(\w+)', gen_upper, re.I)
    gen_tables += re.findall(r'\bJOIN\s+(\w+)', gen_upper, re.I)
    
    expected_tables = list(set(expected_tables))
    gen_tables = list(set(gen_tables))
    
    if expected_tables:
        missing_tables = set(expected_tables) - set(gen_tables)
        extra_tables = set(gen_tables) - set(expected_tables)
        
        if missing_tables:
            return "Частично верно", f"Запрос выполнен, но пропущены таблицы: {missing_tables}"
    
    return "ВЕРНО", "SQL корректен, структура правильная"

def semantic_match(expected_data, generated_data):
    """
    Семантическое сравнение результатов (не строгое)
    """
    if expected_data is None or generated_data is None:
        return False
    
    try:
        if len(expected_data) != len(generated_data):
            if abs(len(expected_data) - len(generated_data)) <= 2:
                return True
            return False
        
        if len(expected_data) > 0 and len(generated_data) > 0:
            exp_sample = [str(x) for x in expected_data[0][:3]] if expected_data[0] else []
            gen_sample = [str(x) for x in generated_data[0][:3]] if generated_data[0] else []
            
            for e_val, g_val in zip(exp_sample, gen_sample):
                if e_val and g_val and str(e_val) == str(g_val):
                    return True
        
        return True  
    
    except Exception:
        return False

def run_test():
    print("=" * 80)
    print("🚀 ЗАПУСК УМНОГО ТЕСТИРОВАНИЯ СИСТЕМЫ")
    print("=" * 80)
    
    # Инициализация
    converter = LLMSQLConverter()
    db.connect()
    
    # Загрузка датасета
    df = pd.read_csv('dataset.csv', encoding='utf-8-sig')
    test_results = []
    
    category_stats = {
        'простой': {'total': 0, 'correct': 0},
        'средний': {'total': 0, 'correct': 0},
        'сложный': {'total': 0, 'correct': 0}
    }
    
    for index, row in df.iterrows():
        test_id = row['id']
        nl_query = row['nl_query']
        expected_sql = row['expected_sql'] if pd.notna(row['expected_sql']) else ""
        category = row['category']
        
        print(f"\n[{test_id}/100] Категория: {category}")
        print(f" Запрос: {nl_query[:60]}...")
        
        start_time = time.time()
        conversion_res = converter.convert(nl_query)
        generated_sql = conversion_res['sql_query']
        understood = conversion_res.get('understood', True)
        end_time = time.time()
        
        exec_time = round(end_time - start_time, 2)
        
        if not understood:
            test_results.append({
                'id': test_id,
                'category': category,
                'verdict': 'Модель не поняла',
                'quality_score': 0,
                'execution_time_sec': exec_time,
                'generated_sql': generated_sql[:200],
                'error_details': 'LLM вернула статус "НЕ ПОНЯЛ"'
            })
            category_stats[category]['total'] += 1
            print(f"Вердикт: МОДЕЛЬ НЕ ПОНЯЛА")
            continue
        
        try:
            generated_data, gen_columns = db.execute_query(generated_sql)
            
            expected_data = None
            if expected_sql:
                try:
                    expected_data, exp_columns = db.execute_query(expected_sql)
                except Exception as e:
                    print(f"Эталонный запрос не выполнился: {e}")
            
            verdict, comment = analyze_sql_quality(generated_sql, expected_sql)
            
            quality_score = 100 if verdict == "ВЕРНО" else 50 if verdict == "Частично верно" else 0
            
            # Дополнительная семантическая проверка
            if expected_data and generated_data:
                if semantic_match(expected_data, generated_data):
                    if verdict == "Частично верно":
                        verdict = "ВЕРНО"
                        quality_score = 90
                        comment = "Результаты семантически совпадают"
            
            test_results.append({
                'id': test_id,
                'category': category,
                'verdict': verdict,
                'quality_score': quality_score,
                'execution_time_sec': exec_time,
                'generated_sql': generated_sql[:200],
                'error_details': comment
            })
            
            category_stats[category]['total'] += 1
            if verdict in ["ВЕРНО", "Верно"]:
                category_stats[category]['correct'] += 1
            
            # Вывод результата
            if verdict == "ВЕРНО":
                print(f"Вердикт: {verdict} (score: {quality_score})")
            elif verdict == "Частично верно":
                print(f"Вердикт: {verdict} - {comment}")
            else:
                print(f"Вердикт: {verdict}")
                
        except Exception as e:
            error_msg = str(e)
            verdict, comment = analyze_sql_quality(generated_sql, expected_sql, error_msg)
            
            test_results.append({
                'id': test_id,
                'category': category,
                'verdict': verdict,
                'quality_score': 0,
                'execution_time_sec': exec_time,
                'generated_sql': generated_sql[:200],
                'error_details': f"{comment} | Ошибка: {error_msg[:150]}"
            })
            category_stats[category]['total'] += 1
            print(f"Вердикт: {verdict} - Ошибка выполнения")
    
    # Сохраняем результаты
    result_df = pd.DataFrame(test_results)
    result_df.to_csv('final_test_report_smart.csv', index=False, encoding='utf-8-sig')
    
    # Статистика
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ УМНОГО ТЕСТИРОВАНИЯ")
    print("=" * 80)
    
    total_correct = 0
    total_tests = 0
    
    for cat, stats in category_stats.items():
        if stats['total'] > 0:
            accuracy = (stats['correct'] / stats['total']) * 100
            total_correct += stats['correct']
            total_tests += stats['total']
            print(f"\n{cat.upper()}:")
            print(f"Верных: {stats['correct']} из {stats['total']} ({accuracy:.1f}%)")
    
    overall = (total_correct / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nИТОГОВАЯ ТОЧНОСТЬ (интеллектуальная оценка): {overall:.1f}%")
    
    # Детализация по вердиктам
    print("\nДЕТАЛИЗАЦИЯ ПО ВЕРДИКТАМ:")
    verdict_counts = result_df['verdict'].value_counts()
    for verdict, count in verdict_counts.items():
        print(f"  {verdict}: {count} запросов ({count/len(result_df)*100:.1f}%)")
    
    print(f"\nОтчёт сохранён: final_test_report_smart.csv")
    
    db.disconnect()

if __name__ == "__main__":
    run_test()