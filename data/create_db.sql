-- 1. Создаем базу данных
-- CREATE DATABASE company_db;

-- 2. Подключаемся к company_db и создаем таблицы
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    patronymic VARCHAR(50),
    department VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2),
    hire_date DATE,
    email VARCHAR(100)
);