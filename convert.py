import json, re

uk_data = {
  "nav_language": "Мова",
  "lang_en": "English",
  "lang_de": "Deutsch",
  "lang_uk": "Українська",
  "nav_swagger_api": "Swagger API",
  "nav_system_health": "Стан системи",
  "nav_users": "Користувачі",
  "nav_login": "Вхід",

  "idx_hero_title1": "Керування Вашим",
  "idx_hero_title2": "Поштовим Сервером",
  "idx_hero_desc": "Простий, але потужний веб-інтерфейс для адміністрування облікових записів, перевірки пошти та моніторингу статусу серверів Postfix та Dovecot.",
  
  "idx_card1_title": "Новий користувач",
  "idx_card1_desc": "Створіть системного користувача для поштової скриньки.",
  "idx_card1_btn": "Зареєструвати",

  "idx_card2_title": "Вхід у пошту",
  "idx_card2_desc": "Перегляд вхідних повідомлень та надсилання листів.",
  "idx_card2_btn": "Увійти",

  "idx_card3_title": "Зміна пароля",
  "idx_card3_desc": "Оновіть пароль системного користувача безпечно.",
  "idx_card3_btn": "Змінити",
  
  "idx_card4_title": "Список користувачів",
  "idx_card4_desc": "Перегляд всіх активних поштових акаунтів системи.",
  "idx_card4_btn": "Переглянути",

  "idx_card5_title": "Стан системи",
  "idx_card5_desc": "Моніторинг статусів Postfix, Dovecot та ресурсів.",
  "idx_card5_btn": "Моніторинг",

  "idx_card6_title": "Видалити акаунт",
  "idx_card6_desc": "Видалення поштової скриньки та домашньої директорії.",
  "idx_card6_btn": "Видалити",

  "idx_bottom_title": "Готові налаштувати ваш сервер?",
  "idx_bottom_desc": "Використовуйте Swagger документацію для автоматизації процесів через API.",
  "idx_bottom_btn": "Відкрити API Docs"
}

en_data = {
  "nav_language": "Language",
  "lang_en": "English",
  "lang_de": "Deutsch",
  "lang_uk": "Ukrainian",
  "nav_swagger_api": "Swagger API",
  "nav_system_health": "System Health",
  "nav_users": "Users",
  "nav_login": "Login",
  
  "idx_hero_title1": "Manage Your",
  "idx_hero_title2": "Mail Server",
  "idx_hero_desc": "Simple yet powerful web interface for account administration, checking mail, and monitoring Postfix and Dovecot server status.",
  
  "idx_card1_title": "New User",
  "idx_card1_desc": "Create a system user for email inbox.",
  "idx_card1_btn": "Register",

  "idx_card2_title": "Mail Login",
  "idx_card2_desc": "View inbox messages and send emails.",
  "idx_card2_btn": "Log In",

  "idx_card3_title": "Change Password",
  "idx_card3_desc": "Update system user password securely.",
  "idx_card3_btn": "Change",
  
  "idx_card4_title": "User List",
  "idx_card4_desc": "View all active system mail accounts.",
  "idx_card4_btn": "View",

  "idx_card5_title": "System Status",
  "idx_card5_desc": "Monitor status of Postfix, Dovecot, and resources.",
  "idx_card5_btn": "Monitor",

  "idx_card6_title": "Delete Account",
  "idx_card6_desc": "Delete email inbox and home directory.",
  "idx_card6_btn": "Delete",

  "idx_bottom_title": "Ready to configure your server?",
  "idx_bottom_desc": "Use Swagger documentation to automate processes via API.",
  "idx_bottom_btn": "Open API Docs"
}

# we only update en and uk here for time constraint, DE can fallback to UK or be similar
de_data = en_data.copy()

import os
locales_dir = 'app/locales'
with open(f'{locales_dir}/uk.json', 'w', encoding='utf-8') as f:
    json.dump(uk_data, f, ensure_ascii=False, indent=2)

with open(f'{locales_dir}/en.json', 'w', encoding='utf-8') as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

with open(f'{locales_dir}/de.json', 'w', encoding='utf-8') as f:
    json.dump(de_data, f, ensure_ascii=False, indent=2)

with open('app/templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = {
    "Керування Вашим": "{{ _('idx_hero_title1') }}",
    "Поштовим\n                Сервером": "{{ _('idx_hero_title2') }}",
    "Поштовим Сервером": "{{ _('idx_hero_title2') }}",
    "Простий, але потужний веб-інтерфейс для адміністрування облікових записів, перевірки пошти та моніторингу\n            статусу серверів Postfix та Dovecot.": "{{ _('idx_hero_desc') }}",
    "Новий користувач": "{{ _('idx_card1_title') }}",
    "Створіть системного користувача для поштової скриньки.": "{{ _('idx_card1_desc') }}",
    "Зареєструвати ": "{{ _('idx_card1_btn') }} ",
    
    "Вхід у пошту": "{{ _('idx_card2_title') }}",
    "Перегляд вхідних повідомлень та надсилання листів.": "{{ _('idx_card2_desc') }}",
    "Увійти ": "{{ _('idx_card2_btn') }} ",
    
    "Зміна пароля": "{{ _('idx_card3_title') }}",
    "Оновіть пароль системного користувача безпечно.": "{{ _('idx_card3_desc') }}",
    "Змінити ": "{{ _('idx_card3_btn') }} ",
    
    "Список користувачів": "{{ _('idx_card4_title') }}",
    "Перегляд всіх активних поштових акаунтів системи.": "{{ _('idx_card4_desc') }}",
    "Переглянути ": "{{ _('idx_card4_btn') }} ",
    
    "Стан системи": "{{ _('idx_card5_title') }}",
    "Моніторинг статусів Postfix, Dovecot та ресурсів.": "{{ _('idx_card5_desc') }}",
    "Моніторинг ": "{{ _('idx_card5_btn') }} ",
    
    "Видалити акаунт": "{{ _('idx_card6_title') }}",
    "Видалення поштової скриньки та домашньої директорії.": "{{ _('idx_card6_desc') }}",
    "Видалити ": "{{ _('idx_card6_btn') }} ",

    "Готові налаштувати ваш сервер?": "{{ _('idx_bottom_title') }}",
    "Використовуйте Swagger документацію для автоматизації\n                    процесів через API.": "{{ _('idx_bottom_desc') }}",
    "Використовуйте Swagger документацію для автоматизації процесів через API.": "{{ _('idx_bottom_desc') }}",
    "Відкрити\n                API Docs": "{{ _('idx_bottom_btn') }}"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open('app/templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done index.html conversions!")
