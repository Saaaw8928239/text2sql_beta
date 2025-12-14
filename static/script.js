// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadSampleQueries();
    updateStats();
});

// Обработка Enter в поле ввода
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        processQuery();
    }
}

// Использовать запрос из истории
function useHistoryQuery(query) {
    document.getElementById('userQuery').value = query;
    processQuery();
}

// Очистить поле ввода
function clearQuery() {
    document.getElementById('userQuery').value = '';
    document.getElementById('userQuery').focus();
}

// Очистить историю
function clearHistory() {
    if (confirm('Вы уверены, что хотите очистить историю запросов?')) {
        fetch('/api/history/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateHistory(data.history || []);
                showMessage('История очищена успешно', 'success');
            }
        });
    }
}

// Показать примеры запросов
function showExamples() {
    const samplesContainer = document.getElementById('sampleQueries');
    if (samplesContainer.style.display === 'none' || samplesContainer.innerHTML === '') {
        fetch('/api/sample_queries')
            .then(response => response.json())
            .then(data => {
                samplesContainer.innerHTML = '';
                data.samples.forEach(query => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<i class="fas fa-play-circle"></i> ${query}`;
                    div.onclick = () => useHistoryQuery(query);
                    samplesContainer.appendChild(div);
                });
                samplesContainer.style.display = 'block';
            });
    } else {
        samplesContainer.style.display = 'none';
    }
}

// Основная функция обработки запроса
function processQuery() {
    const queryInput = document.getElementById('userQuery');
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Пожалуйста, введите запрос');
        return;
    }
    
    // Показать индикатор загрузки
    showLoading(true);
    
    // Засечь время начала
    const startTime = Date.now();
    
    // Отправить запрос на сервер
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            // Обновить SQL запрос с форматированием
            const sqlElement = document.getElementById('sqlQuery');
            if (data.sql_query) {
                sqlElement.textContent = formatSQL(data.sql_query);
            } else {
                sqlElement.textContent = '-- SQL не сгенерирован';
            }
            
            // Обновить историю
            if (data.history) {
                updateHistory(data.history);
            }
            
            // Отобразить результаты
            displayResults(data.results, data.columns);
            
            // Показать статистику выполнения
            const endTime = Date.now();
            const executionTime = endTime - startTime;
            updateExecutionStats(executionTime, data.results ? data.results.length : 0);
            
        } else {
            showError(data.error || 'Неизвестная ошибка');
        }
    })
    .catch(error => {
        showLoading(false);
        showError('Ошибка соединения с сервером: ' + error.message);
    });
}

// Функция для форматирования SQL
function formatSQL(sql) {
    if (!sql || sql.trim() === '') return '-- Нет SQL запроса';
    
    // Простое форматирование SQL для читаемости
    let formatted = sql
        .replace(/SELECT\s+/gi, 'SELECT\n    ')
        .replace(/FROM\s+/gi, '\nFROM\n    ')
        .replace(/WHERE\s+/gi, '\nWHERE\n    ')
        .replace(/GROUP BY\s+/gi, '\nGROUP BY\n    ')
        .replace(/ORDER BY\s+/gi, '\nORDER BY\n    ')
        .replace(/JOIN\s+/gi, '\nJOIN\n    ')
        .replace(/AND\s+/gi, '\n    AND ')
        .replace(/,\s*/g, ',\n    ');
    
    // Удаляем лишние переносы строк
    formatted = formatted.replace(/\n\s*\n/g, '\n');
    
    return formatted;
}

// Отображение результатов в таблице
function displayResults(results, columns) {
    const resultsContainer = document.getElementById('resultsTable');
    
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p class="placeholder">Запрос выполнен успешно, но данных не найдено</p>';
        return;
    }
    
    let html = '<table><thead><tr>';
    
    // Заголовки таблицы
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Данные
    results.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            let value = row[col];
            if (value === null || value === undefined) {
                value = '<span style="color: #94a3b8; font-style: italic;">NULL</span>';
            } else if (typeof value === 'string' && value.includes('₽')) {
                // Для денежных значений
                value = `<span style="color: #059669; font-weight: 500;">${value}</span>`;
            }
            html += `<td>${value}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    resultsContainer.innerHTML = html;
}

// Обновить список истории
function updateHistory(history) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    
    history.forEach(query => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `<i class="fas fa-search"></i> ${query}`;
        div.onclick = () => useHistoryQuery(query);
        historyList.appendChild(div);
    });
}

// Показать/скрыть индикатор загрузки
function showLoading(show) {
    const loading = document.getElementById('loading');
    const submitBtn = document.getElementById('submitBtn');
    
    if (show) {
        loading.style.display = 'block';
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Обработка...';
        submitBtn.disabled = true;
    } else {
        loading.style.display = 'none';
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Выполнить';
        submitBtn.disabled = false;
    }
}

// Показать сообщение об ошибке
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    errorDiv.style.display = 'block';
    
    // Скрыть через 5 секунд
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Показать всплывающее сообщение
function showMessage(message, type = 'success') {
    const div = document.createElement('div');
    div.className = type === 'success' ? 'success-message' : 'error-message';
    div.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle"></i> ${message}`;
    div.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(div);
    
    setTimeout(() => {
        div.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => div.remove(), 300);
    }, 3000);
}

// Копировать SQL в буфер обмена
function copySQL() {
    const sqlText = document.getElementById('sqlQuery').textContent;
    const copyBtn = document.getElementById('copySqlBtn');
    const originalHTML = copyBtn.innerHTML;
    
    // Если SQL пустой, ничего не копируем
    if (!sqlText || sqlText === '-- SQL-запрос появится здесь после обработки' || sqlText === '-- Нет SQL запроса') {
        showError('Нет SQL запроса для копирования');
        return;
    }
    
    navigator.clipboard.writeText(sqlText)
        .then(() => {
            // Показать успешное копирование
            copyBtn.classList.add('copied');
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Скопировано!';
            
            // Восстановить оригинальную кнопку через 2 секунды
            setTimeout(() => {
                copyBtn.classList.remove('copied');
                copyBtn.innerHTML = originalHTML;
            }, 2000);
            
            showMessage('SQL-запрос скопирован в буфер обмена', 'success');
        })
        .catch(err => {
            showError('Не удалось скопировать: ' + err);
        });
}

// Обновить статистику выполнения
function updateExecutionStats(time, rows) {
    document.getElementById('executionTime').innerHTML = 
        `<i class="fas fa-clock"></i> Время выполнения: ${time}мс`;
    
    document.getElementById('rowCount').innerHTML = 
        `<i class="fas fa-chart-bar"></i> Найдено записей: ${rows}`;
}

// Экспорт в CSV
function exportToCSV() {
    const table = document.querySelector('.results-table table');
    if (!table) {
        showError('Нет данных для экспорта');
        return;
    }
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('th, td');
        
        cells.forEach(cell => {
            // Очищаем HTML теги и экранируем запятые
            let text = cell.textContent.replace(/(\r\n|\n|\r)/gm, "").replace(/(\s\s)/gm, " ");
            text = text.replace(/"/g, '""'); // Экранируем кавычки
            if (text.includes(',') || text.includes('"') || text.includes('\n')) {
                text = `"${text}"`;
            }
            rowData.push(text);
        });
        
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'sql_results.csv';
    link.click();
    
    showMessage('Данные экспортированы в CSV', 'success');
}

// Экспорт в PDF (заглушка)
function exportToPDF() {
    showMessage('Экспорт в PDF будет реализован в следующей версии', 'success');
}

// Обновить статистику системы
function updateStats() {
    fetch('/api/db_info')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Статистика БД:', data.stats);
            }
        });
}

// Загрузить примеры запросов
function loadSampleQueries() {
    fetch('/api/sample_queries')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('sampleQueries');
            // Показываем только 5 примеров
            data.samples.slice(0, 5).forEach(query => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `<i class="fas fa-play-circle"></i> ${query}`;
                div.onclick = () => useHistoryQuery(query);
                container.appendChild(div);
            });
        });
}