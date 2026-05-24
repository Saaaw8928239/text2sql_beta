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
        console.log('📦 Ответ от сервера:', data);
        
        if (data.success) {
            // Успешный запрос - отображаем результаты
            const sqlElement = document.getElementById('sqlQuery');
            if (data.sql_query) {
                sqlElement.textContent = formatSQL(data.sql_query);
            } else {
                sqlElement.textContent = '-- SQL не сгенерирован';
            }
            
            // Обновить историю (если есть)
            if (data.history) {
                updateHistory(data.history);
            }
            
            // Сохраняем данные для экспорта!
            window.lastResults = data.formatted_data || data.data;
            window.currentQuery = query;
            
            // Отобразить результаты
            renderTable(data.data, data.columns);
            
            // Показать статистику выполнения
            const endTime = Date.now();
            const executionTime = endTime - startTime;
            updateExecutionStats(executionTime, data.row_count || 0);
            
        } else if (data.blocked) {
            // ⛔ Запрос заблокирован (опасная операция)
            document.getElementById('sqlQuery').textContent = '-- Запрос заблокирован системой безопасности';
            showBlockedError(data.error || 'Запрос заблокирован');
            
            // Очищаем таблицу результатов
            const resultsContainer = document.getElementById('resultsTable');
            resultsContainer.innerHTML = '<p class="placeholder">⛔ Запрос заблокирован системой безопасности</p>';
            
            // Очищаем сохраненные результаты
            window.lastResults = null;
            window.currentQuery = null;
            
        } else if (data.needs_clarification) {
            // ❓ Расплывчатый запрос - показываем подсказки
            document.getElementById('sqlQuery').textContent = '-- Запрос требует уточнения';
            showClarificationDialog(data.message, data.suggestions);
            
            // Очищаем сохраненные результаты
            window.lastResults = null;
            window.currentQuery = null;
            
        } else {
            // Обычная ошибка
            showError(data.error || 'Неизвестная ошибка');
            
            // Очищаем сохраненные результаты
            window.lastResults = null;
            window.currentQuery = null;
        }
    })
    .catch(error => {
        console.error('❌ Ошибка:', error);
        showLoading(false);
        showError('Ошибка соединения с сервером: ' + error.message);
        
        // Очищаем сохраненные результаты при ошибке
        window.lastResults = null;
        window.currentQuery = null;
    });
}

// Функция отрисовки таблицы
function renderTable(results, columns) {
    const resultsContainer = document.getElementById('resultsTable');
    
    console.log('📊 renderTable вызван с:', { results, columns });
    
    // Проверка на пустые данные
    if (!results || results.length === 0) {
        resultsContainer.innerHTML = '<p class="placeholder">Запрос выполнен успешно, но данных не найдено</p>';
        return;
    }
    
    // Проверка на наличие колонок
    if (!columns || columns.length === 0) {
        resultsContainer.innerHTML = '<p class="placeholder">Ошибка: не получены названия колонок</p>';
        return;
    }
    
    let html = '<table class="results-table"><thead><tr>';
    
    // Заголовки таблицы
    columns.forEach(col => {
        html += `<th>${escapeHtml(col)}</th>`;
    });
    html += '</td></thead><tbody>';
    
    // Данные (обрабатываем как массив, а не как объект)
    for (let i = 0; i < results.length; i++) {
        const row = results[i];
        html += '<tr>';
        
        // Проходим по каждой колонке
        for (let j = 0; j < columns.length; j++) {
            let value = row[j];  // Доступ по индексу, а не по ключу
            
            if (value === null || value === undefined) {
                value = '<span style="color: #94a3b8; font-style: italic;">NULL</span>';
            } else if (typeof value === 'number') {
                // Форматируем числа (зарплаты)
                if (value > 10000) {
                    value = new Intl.NumberFormat('ru-RU').format(value) + ' ₽';
                } else {
                    value = new Intl.NumberFormat('ru-RU').format(value);
                }
            } else if (typeof value === 'string') {
                value = escapeHtml(value);
            }
            
            html += `<td>${value}</td>`;
        }
        html += '</tr>';
    }
    
    html += '</tbody></table>';
    resultsContainer.innerHTML = html;
    
    console.log(`✅ Отображено ${results.length} строк`);
}

// Отображение результатов (алиас для совместимости)
function displayResults(results, columns) {
    renderTable(results, columns);
}

// Показать диалог уточнения запроса
function showClarificationDialog(message, suggestions) {
    const resultsContainer = document.getElementById('resultsTable');
    
    let html = '<div class="clarification-box">';
    html += `<p><i class="fas fa-question-circle"></i> ${escapeHtml(message)}</p>`;
    html += '<p><strong>📋 Примеры уточнённых запросов:</strong></p>';
    html += '<ul class="suggestions-list">';
    
    if (suggestions && suggestions.length) {
        suggestions.forEach(suggestion => {
            html += `<li onclick="useHistoryQuery('${escapeHtml(suggestion).replace(/'/g, "\\'")}')">
                        <i class="fas fa-lightbulb"></i> ${escapeHtml(suggestion)}
                    </li>`;
        });
    }
    
    html += '</ul></div>';
    resultsContainer.innerHTML = html;
    
    // Показываем сообщение об ошибке (жёлтое предупреждение)
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<i class="fas fa-question-circle"></i> ${escapeHtml(message)}`;
    errorDiv.style.background = '#fef3c7';
    errorDiv.style.color = '#92400e';
    errorDiv.style.border = '1px solid #f59e0b';
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.style.background = ''; // сброс
        errorDiv.style.color = '';
    }, 8000);
}

// Показать ошибку блокировки
function showBlockedError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<i class="fas fa-shield-alt"></i> ${escapeHtml(message)}`;
    errorDiv.style.background = '#fee2e2';
    errorDiv.style.color = '#dc2626';
    errorDiv.style.border = '1px solid #fca5a5';
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.style.background = '';
        errorDiv.style.color = '';
    }, 8000);
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

// Вспомогательная функция для экранирования HTML
function escapeHtml(text) {
    if (!text) return text;
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Обновить список истории
function updateHistory(history) {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '';
    
    if (!history || history.length === 0) {
        historyList.innerHTML = '<div class="history-empty">История пуста</div>';
        return;
    }
    
    history.forEach(query => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `<i class="fas fa-search"></i> ${escapeHtml(query)}`;
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
function showError(message, duration = 5000) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${escapeHtml(message)}`;
    errorDiv.style.background = '#fee2e2';
    errorDiv.style.color = '#dc2626';
    errorDiv.style.display = 'block';
    
    // Скрыть через указанное время
    setTimeout(() => {
        errorDiv.style.display = 'none';
        errorDiv.style.background = '';
        errorDiv.style.color = '';
    }, duration);
}

// Показать всплывающее сообщение
function showMessage(message, type = 'success') {
    const div = document.createElement('div');
    div.className = type === 'success' ? 'success-message' : 'error-message';
    div.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : 'exclamation'}-circle"></i> ${escapeHtml(message)}`;
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
    if (!sqlText || sqlText === '-- SQL-запрос появится здесь после обработки' || sqlText === '-- Нет SQL запроса' || sqlText === '-- Запрос заблокирован системой безопасности' || sqlText === '-- Запрос требует уточнения') {
        showError('Нет SQL запроса для копирования');
        return;
    }
    
    navigator.clipboard.writeText(sqlText)
        .then(() => {
            copyBtn.classList.add('copied');
            copyBtn.innerHTML = '<i class="fas fa-check"></i> Скопировано!';
            
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

// Экспорт в CSV (с BOM для Excel и разделителем ;)
function exportToCSV() {
    if (!window.lastResults || window.lastResults.length === 0) {
        alert("Сначала выполните запрос, чтобы получить данные!");
        return;
    }

    try {
        const headers = Object.keys(window.lastResults[0]);
        const csvContent = [
            headers.join(';'),
            ...window.lastResults.map(row => 
                headers.map(h => `"${String(row[h] || '').replace(/"/g, '""')}"`).join(';')
            )
        ].join('\r\n');

        // Добавляем \uFEFF (BOM) чтобы Excel понял UTF-8
        const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `export_${new Date().getTime()}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        console.error("Ошибка CSV:", err);
        alert("Ошибка при создании CSV");
    }
}

// Экспорт в PDF (запрос к серверу)
function exportToPDF() {
    if (!window.lastResults || window.lastResults.length === 0) {
        alert("Нет данных для экспорта!");
        return;
    }

    // Показываем лоадер, так как генерация PDF может занять время
    console.log("Отправка данных на генерацию PDF...");

    fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            data: window.lastResults,
            query: window.currentQuery || "Запрос"
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("Ошибка сервера при генерации PDF");
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "report.pdf";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(err => {
        console.error(err);
        alert("Не удалось скачать PDF: " + err.message);
    });
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
            if (container) {
                container.innerHTML = '';
                data.samples.slice(0, 5).forEach(query => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `<i class="fas fa-play-circle"></i> ${escapeHtml(query)}`;
                    div.onclick = () => useHistoryQuery(query);
                    container.appendChild(div);
                });
            }
        });
}