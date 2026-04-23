-- 1. Таблица сотрудников (employees)
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    patronymic VARCHAR(50),
    birth_date DATE,
    gender VARCHAR(10) CHECK (gender IN ('Мужской', 'Женский')),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE NOT NULL,
    termination_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    department_id INTEGER,
    position_id INTEGER,
    manager_id INTEGER,
    salary DECIMAL(10, 2),
    bonus_percent DECIMAL(5, 2) DEFAULT 0
);

-- 2. Таблица отделов (departments)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(10) UNIQUE,
    head_of_department_id INTEGER,
    budget DECIMAL(15, 2),
    location VARCHAR(200),
    phone VARCHAR(20),
    parent_department_id INTEGER,
    created_date DATE DEFAULT CURRENT_DATE
);

-- 3. Таблица должностей (positions)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    position_name VARCHAR(100) NOT NULL UNIQUE,
    position_level VARCHAR(50), -- Junior, Middle, Senior, Lead, Head
    category VARCHAR(50), -- IT, Management, Administrative, Technical
    min_salary DECIMAL(10, 2),
    max_salary DECIMAL(10, 2),
    required_experience_years INTEGER,
    responsibilities TEXT
);

-- 4. Таблица истории изменений должностей и зарплат (employment_history)
CREATE TABLE IF NOT EXISTS employment_history (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    position_id INTEGER,
    department_id INTEGER,
    salary DECIMAL(10, 2),
    start_date DATE NOT NULL,
    end_date DATE,
    change_reason VARCHAR(200)
);

-- 5. Таблица отпусков (vacations)
CREATE TABLE IF NOT EXISTS vacations (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    vacation_type VARCHAR(50), -- Annual, Sick, Unpaid, Educational
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Approved', -- Approved, Pending, Rejected
    approved_by INTEGER,
    comments TEXT
);

-- 6. Таблица премий и бонусов (bonuses)
CREATE TABLE IF NOT EXISTS bonuses (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    bonus_amount DECIMAL(10, 2),
    bonus_date DATE,
    bonus_reason VARCHAR(200),
    quarter INTEGER CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER
);

-- 7. Таблица обучения и курсов (trainings)
CREATE TABLE IF NOT EXISTS trainings (
    id SERIAL PRIMARY KEY,
    training_name VARCHAR(200) NOT NULL,
    training_type VARCHAR(100),
    start_date DATE,
    end_date DATE,
    cost DECIMAL(10, 2),
    provider VARCHAR(200)
);

-- 8. Таблица связи сотрудников с обучением (employee_trainings)
CREATE TABLE IF NOT EXISTS employee_trainings (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    training_id INTEGER NOT NULL,
    completion_date DATE,
    grade VARCHAR(10), -- A, B, C, D, F
    certificate_received BOOLEAN DEFAULT FALSE
);

-- 9. Таблица проектов (projects)
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(200) NOT NULL,
    project_manager_id INTEGER,
    department_id INTEGER,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50), -- Planning, Active, Completed, OnHold, Cancelled
    budget DECIMAL(15, 2)
);

-- 10. Таблица участия сотрудников в проектах (project_assignments)
CREATE TABLE IF NOT EXISTS project_assignments (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role VARCHAR(100),
    hours_allocated INTEGER,
    assignment_date DATE,
    completion_percentage DECIMAL(5, 2) DEFAULT 0
);

-- 11. Таблица оценки эффективности (performance_reviews)
CREATE TABLE IF NOT EXISTS performance_reviews (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    reviewer_id INTEGER,
    review_date DATE,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    goals TEXT,
    next_review_date DATE
);

-- 12. Таблица рекрутинга и вакансий (job_openings)
CREATE TABLE IF NOT EXISTS job_openings (
    id SERIAL PRIMARY KEY,
    position_id INTEGER,
    department_id INTEGER,
    opening_date DATE,
    closing_date DATE,
    status VARCHAR(50), -- Open, Closed, OnHold
    salary_range_min DECIMAL(10, 2),
    salary_range_max DECIMAL(10, 2),
    requirements TEXT,
    candidates_count INTEGER DEFAULT 0
);

-- =====================================================
-- Внешние ключи
-- =====================================================

-- Связи для employees
ALTER TABLE employees ADD CONSTRAINT fk_employees_department 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;
ALTER TABLE employees ADD CONSTRAINT fk_employees_position 
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE SET NULL;
ALTER TABLE employees ADD CONSTRAINT fk_employees_manager 
    FOREIGN KEY (manager_id) REFERENCES employees(id) ON DELETE SET NULL;

-- Связи для departments
ALTER TABLE departments ADD CONSTRAINT fk_departments_head 
    FOREIGN KEY (head_of_department_id) REFERENCES employees(id) ON DELETE SET NULL;
ALTER TABLE departments ADD CONSTRAINT fk_departments_parent 
    FOREIGN KEY (parent_department_id) REFERENCES departments(id) ON DELETE SET NULL;

-- Связи для employment_history
ALTER TABLE employment_history ADD CONSTRAINT fk_history_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
ALTER TABLE employment_history ADD CONSTRAINT fk_history_position 
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE SET NULL;
ALTER TABLE employment_history ADD CONSTRAINT fk_history_department 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

-- Остальные внешние ключи
ALTER TABLE vacations ADD CONSTRAINT fk_vacations_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
ALTER TABLE vacations ADD CONSTRAINT fk_vacations_approved_by 
    FOREIGN KEY (approved_by) REFERENCES employees(id) ON DELETE SET NULL;

ALTER TABLE bonuses ADD CONSTRAINT fk_bonuses_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;

ALTER TABLE employee_trainings ADD CONSTRAINT fk_et_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
ALTER TABLE employee_trainings ADD CONSTRAINT fk_et_training 
    FOREIGN KEY (training_id) REFERENCES trainings(id) ON DELETE CASCADE;

ALTER TABLE projects ADD CONSTRAINT fk_projects_manager 
    FOREIGN KEY (project_manager_id) REFERENCES employees(id) ON DELETE SET NULL;
ALTER TABLE projects ADD CONSTRAINT fk_projects_department 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;

ALTER TABLE project_assignments ADD CONSTRAINT fk_pa_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
ALTER TABLE project_assignments ADD CONSTRAINT fk_pa_project 
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;

ALTER TABLE performance_reviews ADD CONSTRAINT fk_pr_employee 
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE;
ALTER TABLE performance_reviews ADD CONSTRAINT fk_pr_reviewer 
    FOREIGN KEY (reviewer_id) REFERENCES employees(id) ON DELETE SET NULL;

ALTER TABLE job_openings ADD CONSTRAINT fk_jo_position 
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE SET NULL;
ALTER TABLE job_openings ADD CONSTRAINT fk_jo_department 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL;