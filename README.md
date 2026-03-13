# 📧 Mail Service API (FastAPI)

Цей проєкт надає **REST API для керування поштовим сервером**, побудованим на базі **Postfix** та **Dovecot**.  
Система дозволяє створювати та керувати користувачами, змінювати паролі, надсилати та отримувати електронну пошту через **API** або **веб-інтерфейс**.

Рішення орієнтоване на **автоматизацію адміністрування поштового сервера** та інтеграцію з іншими сервісами.

Архітектура включає:

- SMTP-сервер
- IMAP-сервер
- систему фільтрації спаму
- API-шар для програмного доступу до поштових функцій

---

# 🚀 Встановлення та запуск

## 1. Швидке встановлення через Docker (рекомендовано)

Це найпростіший спосіб розгорнути сервер. Скрипт автоматично встановлює залежності, налаштовує поштові служби та запускає API.

### Завантаження конфігурації

```bash
wget -O install_server.sh  https://raw.githubusercontent.com/Bohdan-Nerushev/MailServiceAPI/main/install_server.sh
```

Відкрийте інсталяційний скрипт і вкажіть у ньому необхідні параметри для `.env`.

### Запуск інсталяції

```bash
chmod +x install_server.sh
sudo ./install_server.sh
```

### Що виконує скрипт

- встановлення необхідних системних пакетів
- налаштування **Postfix** і **Dovecot**
- конфігурацію сервісів антиспаму
- запуск контейнерів через **Docker Compose**
- старт **API-сервісу**

Цей варіант оптимальний для **production-середовища**.

---

# 2️⃣ Ручне встановлення (без Docker)

## Клонування репозиторію

```bash
git clone https://github.com/Bohdan-Nerushev/MailServiceAPI.git
cd MailServiceAPI
```

---

## Підготовка Python-середовища

```bash
# Створення віртуального середовища
python3 -m venv venv

# Активація
source venv/bin/activate

# Встановлення залежностей
pip install -r requirements.txt
```

---

## 3️⃣ Налаштування змінних оточення

Створіть файл `.env`:

```bash
nano .env
```

Вкажіть необхідні параметри конфігурації.

---

# ▶️ Запуск застосунку

## Режим розробки

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd) && source venv/bin/activate && python3 app/main.py
```

або через **Uvicorn**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

---

## Production-режим

Для стабільної роботи в production використовується **Gunicorn** з **Uvicorn workers**.

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)

venv/bin/gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8090 \
    --daemon
```
#  Перезавантажити застосунок 
```bash
sudo systemctl restart mail-api
```

---

## Перегляд логів

```bash
tail -f app.log
```

---

## Запуск тестів

```bash
python3 tests/run_all.py
```

---

# 🌐 Endpoints (API та UI)

## API Endpoints (REST JSON)

### System
- `GET /health` — Перевірка стану системи (поштові сервіси, ресурси, метрики)

### Users
- `GET /users/` — Отримання списку всіх користувачів
- `POST /users/` — Створення нового користувача
- `PUT /users/{username}/password` — Зміна пароля користувача
- `DELETE /users/{username}` — Видалення користувача та його поштової скриньки

### Mail
- `POST /mail/send` — Відправлення листа через SMTP
- `GET /mail/inbox/{username}` — Отримання списку листів (INBOX)
- `GET /mail/message/{uid}` — Отримання повного вмісту листа за його UID
- `DELETE /mail/message/{uid}` — Безповоротне видалення листа

---

## UI Endpoints (Web Pages / HTML)

### General & Auth
- `GET /ui/` — Головна сторінка UI
- `GET /ui/login` / `POST /ui/login` — Сторінка та обробка входу
- `GET /ui/register` / `POST /ui/register` — Сторінка та обробка реєстрації
- `GET /ui/change-password` / `POST /ui/change-password` — Зміна пароля
- `GET /ui/delete-user` / `POST /ui/delete-user` — Видалення акаунта
- `POST /ui/logout` — Завершення сесії (вихід)

### Mailbox (Webmail)
- `GET /ui/inbox` — Сторінка поштової скриньки (вхідні, кошик)
- `GET /ui/compose` / `POST /ui/compose` — Сторінка створення та відправка нового листа
- `GET /ui/mail/{uid}` — Перегляд окремого повідомлення
- `POST /ui/mail/{uid}/delete` — Переміщення листа до кошика
- `POST /ui/mail/{uid}/restore` — Відновлення листа з кошика
- `POST /ui/mail/{uid}/permanent-delete` — Безповоротне видалення листа

### System Dashboard
- `GET /ui/health` — Дашборд статусу всіх сервісів (Nginx, Postfix, Dovecot, Spamd)
- `GET /ui/users` — Сторінка зі списком користувачів у системі

---

# 🛠 Технологічний стек

## Backend

- **Python 3.10+** — основна мова розробки
- **FastAPI** — високопродуктивний асинхронний API-фреймворк
- **Uvicorn / Gunicorn** — ASGI сервери для обробки HTTP-запитів
- **Pydantic** — система валідації даних
- **Prometheus FastAPI Instrumentator** — забезпечення метрик
- **python-dotenv / PyYAML** — керування конфігураціями

---

## Робота з поштою

- **imap-tools** — робота з IMAP (читання пошти, керування папками)
- **aiosmtplib** — асинхронне надсилання email через SMTP
- **email-validator** — перевірка email-адрес

---

## Системний моніторинг

- **psutil** — отримання інформації про CPU, RAM і диск

---

## Веб-інтерфейс

- **Jinja2** — шаблонізація HTML
- **Vanilla CSS** — стилізація інтерфейсу

---

## Поштова інфраструктура

- **Postfix** — SMTP сервер
- **Dovecot** — IMAP/POP3 сервер
- **SpamAssassin** — система фільтрації спаму
- **Procmail** — локальна доставка пошти
- **Nginx** — веб-сервер та reverse-proxy (інтегровано для моніторингу стану)

---

# ⚙️ Перегляд налаштувань сервісів

У цьому розділі наведено команди для перевірки поточної конфігурації ключових компонентів системи.

### 🐘 Postfix
Для перегляду всіх діючих (які відрізняються від стандартних) налаштувань Postfix використовуйте команду:
```bash
postconf -n
```
Для перегляду абсолютно всіх налаштувань:
```bash
postconf
```

### 🕊️ Dovecot
Щоб вивести поточну конфігурацію Dovecot (лише активні налаштування, без коментарів):
```bash
doveconf -n
```
Для перегляду всіх налаштувань включно зі стандартними:
```bash
doveconf
```

### 🌐 Nginx
Для перевірки синтаксису конфігурації Nginx та перегляду шляхів до конфігураційних файлів:
```bash
nginx -t

cat  /etc/nginx/sites-enabled/mailservice
```
Щоб вивести на екран усю скомпільовану конфігурацію (разом із усіма включеними файлами `include`):
```bash
nginx -T
```

### 📨 Procmail
Конфігурація Procmail не має вбудованої команди для "дампу" налаштувань. Зазвичай правила обробки листів знаходяться у системному файлі конфігурації. Для перегляду глобальних правил використовуйте:
```bash
cat /etc/procmailrc
```
Або для конкретного користувача:
```bash
cat ~/.procmailrc
```

### 🛡️ SpamAssassin
Щоб перевірити конфігурацію SpamAssassin на наявність синтаксичних помилок:
```bash
spamassassin --lint
```
Щоб переглянути основний конфігураційний файл:
```bash
cat /etc/spamassassin/local.cf
```