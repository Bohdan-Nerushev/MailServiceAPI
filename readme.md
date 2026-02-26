# 📧 Mail Service API (FastAPI)

Цей сервіс надає REST API для керування поштовим сервером (Postfix/Dovecot).

---

## 🚀 Як запустити проект

### 1. Підготовка (один раз)
Переконайтеся, що ви знаходитесь у кореневій папці проекту:
```bash
# Створення віртуального середовища
python3 -m venv venv
# Активація
source venv/bin/activate
# Встановлення залежностей
pip install -r requirements.txt
```

### 2. Запуск програми
Використовуйте цю команду для запуску сервера:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd) && source venv/bin/activate && python3 app/main.py


================
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090 
================

```

---

## 🔗 Адреси сервісу

Після запуску ви знайдете API за наступними адресами:

| Сервіс | Адреса |
| :--- | :--- |
| **API Root** | [http://localhost:8090](http://localhost:8090) |
| **Swagger UI (Документація)** | [http://localhost:8090/docs](http://localhost:8090/docs) |
| **Redocly** | [http://localhost:8090/redoc](http://localhost:8090/redoc) |

---

## 📝 Логування
Усі дії (створення користувачів, відправка та читання пошти) записуються у файл:
`app.log` в кореневій директорії.
