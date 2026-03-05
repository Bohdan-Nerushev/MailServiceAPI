# Використання мінімального, офіційного образу
FROM python:3.11-slim

# Встановлення системних залежностей, необхідних для роботи (якщо потрібні компілятори)
# та очищення кешів apt для зменшення розміру образу
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Створення непривілейованого користувача та відповідної групи для підвищення безпеки
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Встановлення робочої директорії
WORKDIR /app

# Копіювання файлу залежностей та їх встановлення без кешування
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання вихідного коду застосунку
COPY ./app ./app

# Зміна власника файлів на непривілейованого користувача
RUN chown -R appuser:appuser /app

# Перемикання на створеного користувача
USER appuser

# Експозиція порту (для внутрішньої Docker-мережі)
EXPOSE 8090

# Запуск застосунку через Gunicorn з Uvicorn worker-ами (production-ready)
# Припускаємо, що точка входу 'app.main:app'
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8090", "--timeout", "120"]
