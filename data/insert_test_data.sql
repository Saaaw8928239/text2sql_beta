-- =====================================================
-- ТЕСТОВЫЕ ДАННЫЕ ДЛЯ HR БАЗЫ
-- =====================================================

-- =====================================================
-- 1. Заполнение таблицы должностей (positions)
-- =====================================================
INSERT INTO positions (position_name, position_level, category, min_salary, max_salary, required_experience_years, responsibilities) VALUES
('Генеральный директор', 'Executive', 'Management', 500000, 800000, 10, 'Общее руководство компанией, стратегическое планирование'),
('Директор по IT', 'Executive', 'Management', 350000, 500000, 8, 'Руководство IT-департаментом, стратегия цифровизации'),
('Директор по персоналу', 'Executive', 'Management', 300000, 450000, 7, 'Управление HR-процессами, кадровая политика'),
('Руководитель отдела разработки', 'Head', 'Management', 250000, 350000, 6, 'Управление командой разработки, архитектура проектов'),
('Team Lead', 'Lead', 'IT', 200000, 280000, 5, 'Руководство командой, код-ревью, планирование спринтов'),
('Senior разработчик', 'Senior', 'IT', 180000, 250000, 4, 'Разработка сложных модулей, менторство'),
('Middle разработчик', 'Middle', 'IT', 120000, 170000, 2, 'Разработка и поддержка кода, написание тестов'),
('Junior разработчик', 'Junior', 'IT', 70000, 100000, 0, 'Разработка под руководством, изучение технологий'),
('DevOps инженер', 'Senior', 'IT', 190000, 260000, 4, 'CI/CD, администрирование серверов, инфраструктура'),
('Аналитик', 'Middle', 'IT', 110000, 160000, 2, 'Сбор требований, анализ данных, документация'),
('Тестировщик QA', 'Middle', 'Technical', 90000, 140000, 2, 'Тестирование ПО, написание тест-кейсов, баг-трекинг'),
('Системный администратор', 'Middle', 'Technical', 100000, 150000, 3, 'Обслуживание серверов, сетей, рабочих станций'),
('Менеджер проектов', 'Senior', 'Management', 180000, 250000, 4, 'Управление проектами, коммуникация с заказчиками'),
('HR-менеджер', 'Middle', 'Administrative', 100000, 140000, 2, 'Подбор персонала, адаптация, кадровое делопроизводство'),
('Бухгалтер', 'Middle', 'Administrative', 80000, 120000, 3, 'Ведение бухгалтерии, расчёт зарплат, отчётность'),
('Юрист', 'Senior', 'Administrative', 120000, 170000, 4, 'Юридическая поддержка, договора, правовая экспертиза'),
('Офис-менеджер', 'Junior', 'Administrative', 50000, 70000, 1, 'Организация работы офиса, закупки, документооборот'),
('Дизайнер UI/UX', 'Middle', 'Technical', 110000, 160000, 3, 'Проектирование интерфейсов, создание макетов'),
('Data Scientist', 'Senior', 'IT', 200000, 300000, 4, 'Анализ данных, построение моделей машинного обучения'),
('Security специалист', 'Senior', 'Technical', 170000, 240000, 5, 'Обеспечение безопасности, аудит, защита данных');

-- =====================================================
-- 2. Заполнение таблицы отделов (departments)
-- =====================================================
INSERT INTO departments (department_name, department_code, budget, location, phone, parent_department_id) VALUES
('Руководство', 'EXEC', 50000000, 'Москва, ул. Тверская, д.10, 5 этаж', '+7(495)111-11-11', NULL),
('IT Департамент', 'IT', 30000000, 'Москва, ул. Тверская, д.10, 7 этаж', '+7(495)111-11-12', 1),
('Отдел разработки', 'DEV', 20000000, 'Москва, ул. Тверская, д.10, 701 каб', '+7(495)111-11-13', 2),
('Отдел тестирования', 'QA', 8000000, 'Москва, ул. Тверская, д.10, 702 каб', '+7(495)111-11-14', 2),
('Отдел DevOps', 'OPS', 10000000, 'Москва, ул. Тверская, д.10, 703 каб', '+7(495)111-11-15', 2),
('Отдел аналитики', 'ANL', 7000000, 'Москва, ул. Тверская, д.10, 704 каб', '+7(495)111-11-16', 2),
('HR Департамент', 'HR', 8000000, 'Москва, ул. Тверская, д.10, 8 этаж', '+7(495)111-11-20', 1),
('Финансовый департамент', 'FIN', 10000000, 'Москва, ул. Тверская, д.10, 4 этаж', '+7(495)111-11-30', 1),
('Юридический департамент', 'LEG', 6000000, 'Москва, ул. Тверская, д.10, 4 этаж', '+7(495)111-11-31', 1),
('Административный отдел', 'ADM', 5000000, 'Москва, ул. Тверская, д.10, 1 этаж', '+7(495)111-11-40', 1),
('Департамент дизайна', 'DSN', 6000000, 'Москва, ул. Тверская, д.10, 6 этаж', '+7(495)111-11-50', 1);

UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE position_id = (SELECT id FROM positions WHERE position_name = 'Генеральный директор') LIMIT 1) WHERE department_code = 'EXEC';

-- =====================================================
-- 3. Заполнение таблицы сотрудников (employees)
-- =====================================================

-- Генеральный директор
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent) VALUES
('Александр', 'Волков', 'Сергеевич', '1975-03-15', 'Мужской', 'a.volkov@company.ru', '+7(916)111-11-11', '2015-01-10', TRUE, 1, 1, 600000, 50);

-- Директора
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Екатерина', 'Смирнова', 'Андреевна', '1980-07-22', 'Женский', 'e.smirnova@company.ru', '+7(916)111-11-12', '2016-03-01', TRUE, 2, 2, 400000, 40, 1),
('Мария', 'Кузнецова', 'Петровна', '1982-11-05', 'Женский', 'm.kuznetsova@company.ru', '+7(916)111-11-13', '2017-02-15', TRUE, 7, 3, 350000, 35, 1),
('Дмитрий', 'Соколов', 'Игоревич', '1978-09-18', 'Мужской', 'd.sokolov@company.ru', '+7(916)111-11-14', '2015-05-20', TRUE, 8, 3, 320000, 30, 1),
('Ольга', 'Попова', 'Владимировна', '1985-12-10', 'Женский', 'o.popova@company.ru', '+7(916)111-11-15', '2018-01-10', TRUE, 9, 3, 300000, 30, 1);

-- Руководитель отдела разработки и Team Lead'ы
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Андрей', 'Лебедев', 'Михайлович', '1985-04-12', 'Мужской', 'a.lebedev@company.ru', '+7(916)111-11-20', '2016-06-10', TRUE, 3, 4, 300000, 35, 2),
('Павел', 'Новиков', 'Александрович', '1988-08-25', 'Мужской', 'p.novikov@company.ru', '+7(916)222-11-21', '2017-09-01', TRUE, 3, 5, 250000, 25, 6),
('Анна', 'Морозова', 'Сергеевна', '1990-03-18', 'Женский', 'a.morozova@company.ru', '+7(916)222-11-22', '2018-11-15', TRUE, 4, 5, 240000, 25, 2);

-- Senior разработчики
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Максим', 'Васильев', 'Дмитриевич', '1991-02-28', 'Мужской', 'm.vasiliev@company.ru', '+7(916)222-11-23', '2018-03-20', TRUE, 3, 6, 220000, 20, 6),
('Ирина', 'Петрова', 'Алексеевна', '1992-06-14', 'Женский', 'i.petrova@company.ru', '+7(916)222-11-24', '2019-01-15', TRUE, 3, 6, 210000, 20, 7),
('Константин', 'Михайлов', 'Викторович', '1990-11-07', 'Мужской', 'k.mikhailov@company.ru', '+7(916)222-11-25', '2019-07-01', TRUE, 5, 9, 230000, 25, 2),
('Светлана', 'Федорова', 'Евгеньевна', '1993-09-23', 'Женский', 's.fedorova@company.ru', '+7(916)222-11-26', '2020-02-10', TRUE, 3, 6, 200000, 20, 6);

-- Middle разработчики
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Никита', 'Тарасов', 'Ильич', '1995-01-17', 'Мужской', 'n.tarasov@company.ru', '+7(916)333-11-27', '2020-06-20', TRUE, 3, 7, 150000, 15, 7),
('Юлия', 'Белова', 'Дмитриевна', '1996-04-08', 'Женский', 'y.belova@company.ru', '+7(916)333-11-28', '2020-09-15', TRUE, 3, 7, 145000, 15, 6),
('Денис', 'Орлов', 'Андреевич', '1994-12-03', 'Мужской', 'd.orlov@company.ru', '+7(916)333-11-29', '2020-03-25', TRUE, 3, 7, 140000, 15, 7),
('Елена', 'Зайцева', 'Валерьевна', '1995-08-19', 'Женский', 'e.zaitseva@company.ru', '+7(916)333-11-30', '2021-01-20', TRUE, 4, 11, 120000, 15, 8),
('Алексей', 'Медведев', 'Павлович', '1993-07-11', 'Мужской', 'a.medvedev@company.ru', '+7(916)333-11-31', '2019-11-01', TRUE, 5, 9, 190000, 20, 2),
('Татьяна', 'Андреева', 'Николаевна', '1994-10-29', 'Женский', 't.andreeva@company.ru', '+7(916)333-11-32', '2020-04-12', TRUE, 6, 10, 140000, 15, 2);

-- Junior разработчики
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Максим', 'Никитин', 'Романович', '1998-03-21', 'Мужской', 'm.nikitin@company.ru', '+7(916)444-11-33', '2022-02-10', TRUE, 3, 8, 85000, 10, 7),
('Анастасия', 'Соловьева', 'Игоревна', '1999-06-16', 'Женский', 'a.solovieva@company.ru', '+7(916)444-11-34', '2022-08-01', TRUE, 3, 8, 80000, 10, 6),
('Дмитрий', 'Воробьев', 'Сергеевич', '1997-11-27', 'Мужской', 'd.vorobiev@company.ru', '+7(916)444-11-35', '2022-01-15', TRUE, 6, 10, 90000, 10, 2),
('Алина', 'Григорьева', 'Андреевна', '2000-05-02', 'Женский', 'a.grigorieva@company.ru', '+7(916)444-11-36', '2023-03-10', TRUE, 4, 11, 75000, 10, 8);

-- HR и административные сотрудники
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Сергей', 'Козлов', 'Анатольевич', '1987-06-05', 'Мужской', 's.kozlov@company.ru', '+7(916)555-11-37', '2018-08-20', TRUE, 7, 14, 130000, 15, 3),
('Кристина', 'Павлова', 'Ивановна', '1991-09-12', 'Женский', 'k.pavlova@company.ru', '+7(916)555-11-38', '2019-04-25', TRUE, 7, 14, 120000, 15, 3),
('Евгения', 'Семенова', 'Денисовна', '1993-12-18', 'Женский', 'e.semenova@company.ru', '+7(916)555-11-39', '2020-11-10', TRUE, 10, 17, 65000, 10, 1),
('Владимир', 'Егоров', 'Юрьевич', '1985-02-27', 'Мужской', 'v.egorov@company.ru', '+7(916)555-11-40', '2017-07-15', TRUE, 8, 15, 110000, 15, 4),
('Наталья', 'Макарова', 'Сергеевна', '1988-10-14', 'Женский', 'n.makarova@company.ru', '+7(916)555-11-41', '2016-09-01', TRUE, 9, 16, 150000, 20, 5);

-- Сотрудники с увольнениями
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, termination_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Олег', 'Сидоров', 'Владимирович', '1992-11-09', 'Мужской', 'o.sidorov@company.ru', '+7(916)666-11-42', '2019-03-01', '2023-12-20', FALSE, 3, 7, 135000, 15, 7),
('Надежда', 'Иванова', 'Леонидовна', '1990-07-24', 'Женский', 'n.ivanova@company.ru', '+7(916)666-11-43', '2018-05-10', '2023-10-15', FALSE, 7, 14, 125000, 15, 3),
('Игорь', 'Кузьмин', 'Романович', '1989-01-30', 'Мужской', 'i.kuzmin@company.ru', '+7(916)666-11-44', '2019-09-20', '2024-01-31', FALSE, 3, 8, 90000, 10, 7);

-- Дизайнеры
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Алена', 'Алексеева', 'Витальевна', '1992-04-04', 'Женский', 'a.alekseeva@company.ru', '+7(916)777-11-45', '2019-12-01', TRUE, 11, 18, 140000, 15, NULL),
('Артем', 'Лебедев', 'Андреевич', '1995-08-16', 'Мужской', 'a.lebedev_des@company.ru', '+7(916)777-11-46', '2021-07-15', TRUE, 11, 18, 120000, 15, 27);

-- Data Scientist
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Михаил', 'Сергеев', 'Владиславович', '1991-11-11', 'Мужской', 'm.sergeev@company.ru', '+7(916)888-11-47', '2020-05-18', TRUE, 6, 19, 220000, 25, 2);

-- Security
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Евгений', 'Баранов', 'Александрович', '1988-08-08', 'Мужской', 'e.baranov@company.ru', '+7(916)999-11-48', '2019-10-01', TRUE, 2, 20, 200000, 20, 2);

-- Системный администратор
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Роман', 'Титов', 'Александрович', '1993-03-03', 'Мужской', 'r.titov@company.ru', '+7(916)000-11-49', '2020-02-20', TRUE, 2, 12, 120000, 15, 2);

-- Project Manager
INSERT INTO employees (first_name, last_name, patronymic, birth_date, gender, email, phone, hire_date, is_active, department_id, position_id, salary, bonus_percent, manager_id) VALUES
('Оксана', 'Крылова', 'Владимировна', '1987-07-19', 'Женский', 'o.krylova@company.ru', '+7(916)111-11-50', '2017-08-01', TRUE, 3, 13, 220000, 20, 6);

-- Обновляем руководителей отделов
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'e.smirnova@company.ru') WHERE department_code = 'IT';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'm.kuznetsova@company.ru') WHERE department_code = 'HR';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'd.sokolov@company.ru') WHERE department_code = 'FIN';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'o.popova@company.ru') WHERE department_code = 'LEG';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'a.lebedev@company.ru') WHERE department_code = 'DEV';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'a.morozova@company.ru') WHERE department_code = 'QA';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'k.mikhailov@company.ru') WHERE department_code = 'OPS';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 't.andreeva@company.ru') WHERE department_code = 'ANL';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'e.semenova@company.ru') WHERE department_code = 'ADM';
UPDATE departments SET head_of_department_id = (SELECT id FROM employees WHERE email = 'a.alekseeva@company.ru') WHERE department_code = 'DSN';

-- =====================================================
-- 4. История изменений должностей и зарплат
-- =====================================================
INSERT INTO employment_history (employee_id, position_id, department_id, salary, start_date, end_date, change_reason) VALUES
(1, 1, 1, 600000, '2015-01-10', NULL, 'Принят на должность'),
(2, 2, 2, 400000, '2016-03-01', NULL, 'Принята на должность'),
(6, 4, 3, 300000, '2016-06-10', NULL, 'Назначен руководителем отдела разработки'),
(7, 5, 3, 250000, '2017-09-01', NULL, 'Принят на должность Team Lead'),
(10, 6, 3, 180000, '2018-03-20', '2021-01-15', 'Повышение до Middle'),
(10, 7, 3, 120000, '2021-01-16', NULL, 'Повышение до Senior'),
(16, 8, 3, 85000, '2022-02-10', NULL, 'Принят на должность'),
(31, 8, 3, 80000, '2022-08-01', NULL, 'Принята на должность'),
(24, 14, 7, 120000, '2019-04-25', NULL, 'Принята на должность'),
(25, 17, 10, 65000, '2020-11-10', NULL, 'Принята на должность'),
(26, 15, 8, 110000, '2017-07-15', NULL, 'Принят на должность'),
(27, 16, 9, 150000, '2016-09-01', NULL, 'Принята на должность'),
(28, 7, 3, 135000, '2019-03-01', '2023-12-20', 'Уволен'),
(29, 14, 7, 125000, '2018-05-10', '2023-10-15', 'Уволена'),
(30, 8, 3, 90000, '2019-09-20', '2024-01-31', 'Уволен');

-- =====================================================
-- 5. Отпуска
-- =====================================================
INSERT INTO vacations (employee_id, vacation_type, start_date, end_date, status, comments) VALUES
(1, 'Annual', '2024-07-01', '2024-07-14', 'Approved', 'Ежегодный отпуск'),
(2, 'Annual', '2024-08-10', '2024-08-24', 'Approved', 'Отпуск'),
(6, 'Annual', '2024-06-15', '2024-06-30', 'Approved', 'Отпуск'),
(7, 'Sick', '2024-02-05', '2024-02-12', 'Approved', 'Больничный'),
(10, 'Annual', '2024-09-01', '2024-09-15', 'Pending', 'Запланированный отпуск'),
(11, 'Unpaid', '2024-03-10', '2024-03-20', 'Approved', 'Отпуск без содержания'),
(12, 'Annual', '2024-05-20', '2024-06-05', 'Approved', 'Отпуск'),
(13, 'Sick', '2024-01-15', '2024-01-22', 'Approved', 'Больничный'),
(14, 'Educational', '2024-10-01', '2024-10-14', 'Approved', 'Сессия'),
(16, 'Annual', '2024-07-15', '2024-07-29', 'Approved', 'Отпуск'),
(17, 'Annual', '2024-08-05', '2024-08-19', 'Rejected', 'Отказано'),
(18, 'Sick', '2024-04-01', '2024-04-07', 'Approved', 'Больничный');

-- =====================================================
-- 6. Премии и бонусы
-- =====================================================
INSERT INTO bonuses (employee_id, bonus_amount, bonus_date, bonus_reason, quarter, year) VALUES
(1, 300000, '2024-03-31', 'Премия по итогам квартала', 1, 2024),
(2, 200000, '2024-03-31', 'Премия по итогам квартала', 1, 2024),
(6, 150000, '2024-03-31', 'Премия по итогам квартала', 1, 2024),
(7, 120000, '2024-03-31', 'За успешный проект', 1, 2024),
(10, 100000, '2024-06-30', 'Премия по итогам квартала', 2, 2024),
(11, 80000, '2024-06-30', 'За хорошую работу', 2, 2024),
(12, 75000, '2024-06-30', 'Премия', 2, 2024),
(1, 350000, '2024-12-20', 'Годовая премия', 4, 2024),
(2, 250000, '2024-12-20', 'Годовая премия', 4, 2024),
(3, 200000, '2024-12-20', 'Годовая премия', 4, 2024),
(6, 180000, '2024-12-20', 'Годовая премия', 4, 2024),
(27, 80000, '2024-12-20', 'Годовая премия', 4, 2024),
(7, 60000, '2023-12-20', 'Годовая премия 2023', 4, 2023),
(10, 50000, '2023-12-20', 'Годовая премия 2023', 4, 2023);

-- =====================================================
-- 7. Обучения и курсы
-- =====================================================
INSERT INTO trainings (training_name, training_type, start_date, end_date, cost, provider) VALUES
('Python для продвинутых', 'Программирование', '2024-02-01', '2024-03-15', 50000, 'Skillbox'),
('DevOps практики', 'Инфраструктура', '2024-03-10', '2024-04-20', 75000, 'Слёрм'),
('Управление проектами PMP', 'Управление', '2024-01-15', '2024-02-28', 90000, 'Нетология'),
('SQL для аналитиков', 'Данные', '2023-11-01', '2023-12-15', 30000, 'Тензор'),
('Тестирование Java-приложений', 'Тестирование', '2024-04-01', '2024-05-01', 40000, 'Отус'),
('Machine Learning базовый', 'Машинное обучение', '2024-09-01', '2024-10-15', 100000, 'Яндекс.Практикум'),
('Английский для IT', 'Языки', '2024-01-10', '2024-12-20', 60000, 'EnglishDom'),
('Лидерство и управление командой', 'Soft skills', '2024-05-15', '2024-06-30', 45000, 'Школа лидерства'),
('Кибербезопасность', 'Безопасность', '2024-10-01', '2024-11-20', 80000, 'OTUS'),
('Agile и Scrum', 'Управление', '2024-03-01', '2024-04-15', 55000, 'Нетология');

-- =====================================================
-- 8. Обучение сотрудников
-- =====================================================
INSERT INTO employee_trainings (employee_id, training_id, completion_date, grade, certificate_received) VALUES
(10, 1, '2024-03-14', 'A', TRUE),
(11, 1, '2024-03-14', 'B', TRUE),
(12, 1, '2024-03-14', 'C', TRUE),
(13, 1, '2024-03-11', 'F', FALSE),
(2, 3, '2024-02-25', 'A', TRUE),
(6, 3, '2024-02-26', 'B', TRUE),
(7, 4, '2023-12-10', 'A', TRUE),
(16, 4, '2023-12-12', 'B', TRUE),
(11, 5, '2024-04-28', 'A', TRUE),
(14, 5, '2024-04-30', 'B', TRUE),
(33, 6, '2024-10-05', 'A', TRUE),
(8, 8, '2024-06-25', 'A', TRUE),
(1, 8, '2024-06-28', 'A', TRUE);

-- =====================================================
-- 9. Проекты
-- =====================================================
INSERT INTO projects (project_name, project_manager_id, department_id, start_date, end_date, status, budget) VALUES
('Мобильное приложение "Банк-Онлайн"', 35, 3, '2023-09-01', '2024-12-31', 'Active', 5000000),
('Обновление CRM системы', 35, 3, '2024-01-10', '2024-08-31', 'Active', 3000000),
('Автоматизация HR процессов', 24, 7, '2024-02-01', '2024-11-30', 'Active', 1500000),
('Дашборды для финансового отдела', 35, 6, '2024-03-15', '2024-07-31', 'Planning', 1000000),
('Миграция в облако', 35, 5, '2024-04-01', '2024-10-31', 'Active', 2500000),
('Система безопасности DataGuard', 33, 2, '2024-01-20', '2024-09-30', 'Active', 2000000),
('Сайт компании (редизайн)', 35, 11, '2024-05-01', '2024-08-15', 'Planning', 800000),
('AI-ассистент для техподдержки', 33, 6, '2024-06-01', '2025-03-31', 'Active', 4000000),
('Проект законченный', 35, 3, '2023-01-01', '2023-12-31', 'Completed', 2000000),
('Проект отложенный', 35, 3, '2024-02-01', '2024-12-31', 'OnHold', 1500000);

-- =====================================================
-- 10. Участие в проектах (продолжение)
-- =====================================================
INSERT INTO project_assignments (employee_id, project_id, role, hours_allocated, assignment_date, completion_percentage) VALUES
(6, 1, 'Руководитель проекта', 160, '2023-09-01', 85),
(7, 1, 'Team Lead', 160, '2023-09-01', 85),
(10, 1, 'Senior разработчик', 150, '2023-09-01', 85),
(11, 1, 'Middle разработчик', 150, '2023-09-01', 80),
(12, 1, 'Middle разработчик', 140, '2023-09-15', 75),
(16, 1, 'Junior разработчик', 120, '2023-10-01', 70),
(13, 2, 'Senior разработчик', 160, '2024-01-10', 60),
(14, 2, 'Middle разработчик', 150, '2024-01-15', 55),
(15, 2, 'Тестировщик', 100, '2024-01-20', 50),
(16, 2, 'Junior разработчик', 120, '2024-02-01', 45),
(24, 3, 'HR-менеджер', 80, '2024-02-01', 40),
(25, 3, 'Офис-менеджер', 60, '2024-02-01', 40),
(10, 4, 'Аналитик данных', 100, '2024-03-15', 30),
(33, 4, 'Data Scientist', 120, '2024-03-20', 35),
(12, 5, 'DevOps инженер', 160, '2024-04-01', 45),
(13, 5, 'DevOps инженер', 140, '2024-04-01', 40),
(33, 6, 'Security специалист', 160, '2024-01-20', 65),
(34, 6, 'Системный администратор', 120, '2024-01-20', 60),
(27, 7, 'Дизайнер UI/UX', 100, '2024-05-01', 20),
(28, 7, 'Дизайнер UI/UX', 80, '2024-05-01', 20),
(33, 8, 'Data Scientist', 160, '2024-06-01', 25),
(10, 8, 'Аналитик', 120, '2024-06-10', 20),
(11, 9, 'Middle разработчик', 140, '2023-01-01', 100),
(12, 9, 'Middle разработчик', 130, '2023-01-01', 100),
(14, 9, 'Тестировщик', 100, '2023-01-15', 100),
(6, 10, 'Руководитель проекта', 80, '2024-02-01', 10),
(7, 10, 'Team Lead', 60, '2024-02-15', 10);

-- =====================================================
-- 11. Оценка эффективности (performance_reviews)
-- =====================================================
INSERT INTO performance_reviews (employee_id, reviewer_id, review_date, rating, comments, goals, next_review_date) VALUES
(6, 2, '2023-12-15', 5, 'Отличная работа, проект успешно выполнен', 'Повысить квалификацию до Architect', '2024-12-15'),
(7, 6, '2023-12-10', 4, 'Хорошее управление командой', 'Улучшить метрики качества кода', '2024-12-10'),
(10, 7, '2023-12-05', 5, 'Выдающиеся результаты, менторство джуниоров', 'Стать Team Lead', '2024-12-05'),
(11, 7, '2023-12-05', 4, 'Хорошая скорость разработки', 'Углубить знание архитектуры', '2024-12-05'),
(12, 7, '2023-12-05', 3, 'Средние результаты, требует доработки', 'Повысить качество кода', '2024-12-05'),
(13, 2, '2023-12-20', 5, 'Отличная работа над инфраструктурой', 'Сертификация Kubernetes', '2024-12-20'),
(14, 8, '2023-12-18', 4, 'Хороший тестировщик', 'Автоматизация тестирования', '2024-12-18'),
(16, 7, '2023-12-05', 4, 'Перспективный джуниор', 'Изучить фреймворки', '2024-12-05'),
(24, 3, '2023-12-10', 5, 'Отличный HR-менеджер', 'Развитие бренда работодателя', '2024-12-10'),
(25, 1, '2023-12-01', 4, 'Хорошая офисная работа', 'Улучшить процессы закупок', '2024-12-01'),
(26, 4, '2023-12-12', 4, 'Надёжный бухгалтер', 'Автоматизация отчётности', '2024-12-12'),
(27, 5, '2023-12-14', 5, 'Профессиональный юрист', 'Участие в судебных процессах', '2024-12-14'),
(33, 2, '2024-06-01', 5, 'Отличные навыки ML', 'Публикация статьи', '2024-12-01'),
(34, 2, '2024-06-01', 4, 'Хороший администратор', 'Автоматизация рутины', '2024-12-01'),
(35, 6, '2024-06-15', 5, 'Отличный PM, проекты в сроке', 'Сертификация PMP', '2024-12-15'),
(1, 1, '2023-12-20', 5, 'Стратегическое видение компании', 'Выход на новые рынки', '2024-12-20'),
(2, 1, '2023-12-20', 5, 'IT-департамент показывает высокие результаты', 'Цифровая трансформация', '2024-12-20'),
(3, 1, '2023-12-20', 4, 'Хорошая работа с персоналом', 'Снижение текучести', '2024-12-20');

-- =====================================================
-- 12. Вакансии (job_openings)
-- =====================================================
INSERT INTO job_openings (position_id, department_id, opening_date, closing_date, status, salary_range_min, salary_range_max, requirements, candidates_count) VALUES
((SELECT id FROM positions WHERE position_name = 'Senior разработчик'), (SELECT id FROM departments WHERE department_code = 'DEV'), '2024-01-10', '2024-03-31', 'Closed', 180000, 250000, 'Опыт от 4 лет, знание Python/Java, PostgreSQL', 45),
((SELECT id FROM positions WHERE position_name = 'Middle разработчик'), (SELECT id FROM departments WHERE department_code = 'DEV'), '2024-02-01', '2024-04-30', 'Open', 120000, 170000, 'Опыт от 2 лет, готовность к переезду', 28),
((SELECT id FROM positions WHERE position_name = 'Тестировщик QA'), (SELECT id FROM departments WHERE department_code = 'QA'), '2024-03-01', '2024-05-31', 'Open', 90000, 140000, 'Опыт ручного и автотестирования', 32),
((SELECT id FROM positions WHERE position_name = 'DevOps инженер'), (SELECT id FROM departments WHERE department_code = 'OPS'), '2024-04-15', '2024-06-30', 'Open', 190000, 260000, 'K8s, CI/CD, облачные технологии', 19),
((SELECT id FROM positions WHERE position_name = 'Аналитик'), (SELECT id FROM departments WHERE department_code = 'ANL'), '2024-05-01', '2024-07-15', 'Open', 110000, 160000, 'SQL, визуализация данных, аналитическое мышление', 23),
((SELECT id FROM positions WHERE position_name = 'HR-менеджер'), (SELECT id FROM departments WHERE department_code = 'HR'), '2023-11-01', '2024-01-31', 'Closed', 100000, 140000, 'Опыт подбора IT-специалистов', 56),
((SELECT id FROM positions WHERE position_name = 'Дизайнер UI/UX'), (SELECT id FROM departments WHERE department_code = 'DSN'), '2024-06-01', '2024-08-31', 'Open', 110000, 160000, 'Портфолио, Figma, пользовательские исследования', 41),
((SELECT id FROM positions WHERE position_name = 'Junior разработчик'), (SELECT id FROM departments WHERE department_code = 'DEV'), '2024-05-15', '2024-07-31', 'OnHold', 70000, 100000, 'Высшее образование, базовые знания', 87),
((SELECT id FROM positions WHERE position_name = 'Security специалист'), (SELECT id FROM departments WHERE department_code = 'IT'), '2024-03-10', '2024-06-30', 'Open', 170000, 240000, 'Опыт аудита безопасности', 15);


UPDATE employees SET manager_id = (SELECT id FROM employees WHERE email = 'a.volkov@company.ru') WHERE position_id IN (SELECT id FROM positions WHERE position_level IN ('Executive', 'Head'));
UPDATE employees SET manager_id = (SELECT id FROM employees WHERE email = 'o.krylova@company.ru') WHERE department_id = (SELECT id FROM departments WHERE department_code = 'DEV') AND position_id IN (SELECT id FROM positions WHERE position_name IN ('Senior разработчик', 'Middle разработчик', 'Junior разработчик'));

-- Фикс для Artem Lebedev (дизайнера)
UPDATE employees SET manager_id = (SELECT id FROM employees WHERE email = 'a.alekseeva@company.ru') WHERE email = 'a.lebedev_des@company.ru';