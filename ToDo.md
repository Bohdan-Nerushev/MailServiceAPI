# План розробки Mail Service API (FastAPI)

Цей проект автоматизує керування поштовим сервером (Postfix/Dovecot) через REST API.

---

## 🟢 Фаза 1: Підготовка та ініціалізація
- [x] **Ініціалізація проекту через Poetry**:
    - `poetry init`
    - Додавання залежностей: `fastapi`, `uvicorn`, `aiosmtplib`, `imap_tools`, `python-dotenv`.
- [x] **Створення структури папок**:
    - `app/main.py` (точка входу)
    - `app/services/` (логіка SMTP, IMAP, Linux Users)
    - `app/routes/` (ендпоінти API)
    - `.env` (конфігурація серверів та портів)
- [x] **Налаштування "Hello World"**:
    - Базовий запуск FastAPI та перевірка доступу до `/docs` (Swagger).

---

## 🔵 Фаза 2: Керування користувачами (Subprocess)
*Мета: автоматизація консольних команд `useradd`, `passwd` тощо.*
- [x] Створення модуля `services/user_manager.py`.
- [x] Реалізація функцій через `subprocess.run`:
    - `create_system_user(username, password)`
    - `delete_system_user(username)`
    - `change_user_password(username, new_password)`
- [x] **Налаштування Sudo**: 
    - Додавання прав для користувача, від якого працює API, на виконання конкретних команд без пароля (`visudo`).

---

## 🟡 Фаза 3: Надсилання пошти (SMTP + aiosmtplib)
*Мета: надсилання листів через локальний Postfix.*
- [x] Створення модуля `services/smtp_service.py`.
- [x] Налаштування асинхронного клієнта `aiosmtplib`.
- [x] Створення ендпоінта `POST /mail/send`:
    - Прийом JSON (to, subject, body).
    - Валідація даних через Pydantic.

---

## 🟣 Фаза 4: Читання пошти (IMAP + imap_tools)
*Мета: доступ до поштових скриньок через Dovecot.*
- [x] Створення модуля `services/imap_service.py`.
- [x] Реалізація підключення до `localhost` через `imap_tools`.
- [x] Створення ендпоінтів:
    - `GET /mail/inbox/{username}` — список заголовків останніх листів.
    - `GET /mail/message/{id}` — отримання повного тексту конкретного листа.

---

## 🔴 Фаза 5: Безпека та логування
- [x] **Логування**:
    - Запис усіх дій (хто, коли і кому відправив лист) у лог-файл.

---

## 🏁 Фаза 6: Фіналізація та тестування
- [ ] Тестування повного циклу: Створення юзера -> Надсилання листа -> Читання листа (все через Swagger).
- [ ] Створення `systemd` сервісу для автозапуску API разом із сервером.


## 🛡️ Фаза 7: Антиспам та фільтрація (SpamAssassin + Procmail)
*Мета: автоматична перевірка пошти на спам та можливість кастомної фільтрації.*

### 1. SpamAssassin (Антиспам)
- [ ] **Встановлення та налаштування**:
    - `sudo apt install spamassassin spamc`
    - Увімкнення сервісу: `systemctl enable spamassassin`
- [ ] **Інтеграція з Postfix**:
    - Налаштувати `master.cf` для передачі пошти через `spamc` перед доставкою.
    - Перевірка: додавання заголовків `X-Spam-Status` до вхідних листів.

### 2. Procmail (Фільтрація)
- [ ] **Встановлення**: `sudo apt install procmail`
- [ ] **Інтеграція з Postfix**:
    - Налаштувати `mailbox_command = /usr/bin/procmail -a "$EXTENSION"` у `main.cf`.
- [ ] **Глобальна та персональна конфігурація**:
    - Створення глобального `/etc/procmailrc` для базових правил.
    - Підтримка індивідуальних `.procmailrc` у домашніх директоріях користувачів.

### 3. API Розширення (FastAPI)
- [ ] **Керування фільтрами користувача**:
    - `GET /users/{username}/filters` — читання вмісту `.procmailrc`.
    - `PUT /users/{username}/filters` — оновлення правил фільтрації.
- [ ] **Статус сервісів**:
    - Додати перевірку статусу `spamassassin` у ендпоінт `/health`.
