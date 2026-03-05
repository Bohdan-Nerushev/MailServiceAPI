import json

# Load existing JSON
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

uk = load_json('app/locales/uk.json')
en = load_json('app/locales/en.json')
de = load_json('app/locales/de.json')

# New translations
translations = {
    # register.html
    "reg_title": ("Новий користувач", "New User", "Neuer Benutzer"),
    "reg_username": ("Ім'я користувача", "Username", "Benutzername"),
    "reg_password": ("Пароль", "Password", "Passwort"),
    "reg_confirm": ("Підтвердіть пароль", "Confirm Password", "Passwort bestätigen"),
    "reg_submit": ("Створити акаунт", "Create Account", "Konto erstellen"),
    "reg_important": ("Важливо", "Important", "Wichtig"),
    "reg_info": ("Ця дія також створить домашню директорію користувача в системі Linux для зберігання пошти.", "This action will also create a home directory for the user in the Linux system to store mail.", "Diese Aktion erstellt auch ein Heimatverzeichnis für den Benutzer im Linux-System zum Speichern von E-Mails."),
    
    # users_list.html
    "users_title": ("Поштові акаунти", "Mail Accounts", "E-Mail-Konten"),
    "users_desc": ("Перегляд активних користувачів та їх директорій", "View active users and their directories", "Aktive Benutzer und ihre Verzeichnisse anzeigen"),
    "users_add": ("Додати", "Add", "Hinzufügen"),
    "users_col_user": ("Користувач", "User", "Benutzer"),
    "users_col_dir": ("Домашня Директорія", "Home Directory", "Heimatverzeichnis"),
    "users_col_actions": ("Дії", "Actions", "Aktionen"),
    "users_change_pass": ("Змінити пароль", "Change Password", "Passwort ändern"),
    "users_delete": ("Видалити", "Delete", "Löschen"),
    "users_not_found": ("Користувачів поки не знайдено", "No users found yet", "Noch keine Benutzer gefunden"),
    
    # health.html
    "health_title": ("Моніторинг сервісів", "Services Monitoring", "Dienste-Überwachung"),
    "health_updated_at": ("Дані актуальні на", "Data current as of", "Daten aktuell ab"),
    "health_refresh": ("Оновити", "Refresh", "Aktualisieren"),
    "health_api_service": ("API Сервіс", "API Service", "API-Dienst"),
    "health_details": ("Детальніше", "Details", "Details"),
    "health_config": ("Конфігурація", "Configuration", "Konfiguration"),
    "health_acc_state": ("Стан акаунтів", "Accounts State", "Kontostatus"),
    "health_sys": ("Система", "System", "System"),
    "health_os_load": ("Завантаження ОС", "OS Load", "OS-Auslastung"),
    "health_net_ifaces": ("Мережеві інтерфейси", "Network Interfaces", "Netzwerkschnittstellen"),
    "health_name": ("Назва", "Name", "Name"),
    "health_ip": ("IP Адреса", "IP Address", "IP-Adresse"),
    "health_mask": ("Маска", "Mask", "Maske"),
    "health_fw": ("Берандмауер (UFW)", "Firewall (UFW)", "Firewall (UFW)"),
    "health_ports": ("Активні порти", "Active Ports", "Aktive Ports"),
    "health_os_params": ("Параметри ОС", "OS Parameters", "OS-Parameter"),
    "health_kernel": ("Версія ядра", "Kernel Version", "Kernel-Version"),
    "health_ram": ("Оперативна пам'ять", "RAM", "RAM"),
    "health_server_cfg": ("Конфігурація сервера", "Server Configuration", "Serverkonfiguration"),
    "health_postfix_cfg": ("Конфігурація Postfix", "Postfix Configuration", "Postfix-Konfiguration"),
    "health_dovecot_cfg": ("Конфігурація Dovecot", "Dovecot Configuration", "Dovecot-Konfiguration"),
    "health_api_params": ("Параметри API", "API Parameters", "API-Parameter"),
    "health_sys_resources": ("Ресурси Системи", "System Resources", "Systemressourcen"),
    "health_close": ("Закрити", "Close", "Schließen")
}

for k, (u, e, d) in translations.items():
    uk[k] = u
    en[k] = e
    de[k] = d

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

save_json(uk, 'app/locales/uk.json')
save_json(en, 'app/locales/en.json')
save_json(de, 'app/locales/de.json')

# Helper to read and write content
def process_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# register.html replacements
reg_replacements = {
    ">Новий користувач<": ">{{ _('reg_title') }}<",
    ">Ім'я користувача<": ">{{ _('reg_username') }}<",
    ">Пароль<": ">{{ _('reg_password') }}<",
    ">Підтвердіть\\n                    пароль<": ">{{ _('reg_confirm') }}<",
    ">Підтвердіть\n                    пароль<": ">{{ _('reg_confirm') }}<",
    "Підтвердіть\\n                    пароль": "{{ _('reg_confirm') }}",
    "Підтвердіть\n                    пароль": "{{ _('reg_confirm') }}",
    ">Створити акаунт<": ">{{ _('reg_submit') }}<",
    "\n                Створити акаунт\n": "\n                {{ _('reg_submit') }}\n",
    ">Важливо<": ">{{ _('reg_important') }}<",
    "Ця дія також створить домашню директорію користувача в системі\\n                    Linux для зберігання пошти.": "{{ _('reg_info') }}",
    "Ця дія також створить домашню директорію користувача в системі\n                    Linux для зберігання пошти.": "{{ _('reg_info') }}"
}
process_file('app/templates/register.html', reg_replacements)

# users_list.html replacements
users_replacements = {
    ">Поштові акаунти<": ">{{ _('users_title') }}<",
    ">Перегляд активних користувачів та їх директорій<": ">{{ _('users_desc') }}<",
    "\n            Додати\n": "\n            {{ _('users_add') }}\n",
    ">Користувач<": ">{{ _('users_col_user') }}<",
    ">Домашня Директорія<": ">{{ _('users_col_dir') }}<",
    ">Дії<": ">{{ _('users_col_actions') }}<",
    "title=\"Змінити пароль\"": "title=\"{{ _('users_change_pass') }}\"",
    "title=\"Видалити\"": "title=\"{{ _('users_delete') }}\"",
    ">Користувачів поки не знайдено<": ">{{ _('users_not_found') }}<"
}
process_file('app/templates/users_list.html', users_replacements)

# health.html replacements
health_replacements = {
    ">Моніторинг сервісів<": ">{{ _('health_title') }}<",
    "Дані актуальні на ": "{{ _('health_updated_at') }} ",
    ">Оновити<": ">{{ _('health_refresh') }}<",
    ">API Сервіс<": ">{{ _('health_api_service') }}<",
    "\n                Детальніше\n": "\n                {{ _('health_details') }}\n",
    "\n                Конфігурація\n": "\n                {{ _('health_config') }}\n",
    "\n                Стан акаунтів\n": "\n                {{ _('health_acc_state') }}\n",
    ">Система<": ">{{ _('health_sys') }}<",
    "\n                Завантаження ОС\n": "\n                {{ _('health_os_load') }}\n",
    "Мережеві інтерфейси\n": "{{ _('health_net_ifaces') }}\n",
    ">Назва<": ">{{ _('health_name') }}<",
    ">IP Адреса<": ">{{ _('health_ip') }}<",
    ">Маска<": ">{{ _('health_mask') }}<",
    "Берандмауер (UFW)\n": "{{ _('health_fw') }}\n",
    "Активні порти\n": "{{ _('health_ports') }}\n",
    "Параметри ОС<": "{{ _('health_os_params') }}<",
    ">Версія ядра<": ">{{ _('health_kernel') }}<",
    ">Оперативна пам'ять<": ">{{ _('health_ram') }}<",
    "Конфігурація сервера\n": "{{ _('health_server_cfg') }}\n",
    "'Конфігурація Postfix'": "'{{ _(\\'health_postfix_cfg\\') }}'",
    "'Конфігурація Dovecot'": "'{{ _(\\'health_dovecot_cfg\\') }}'",
    "'Параметри API'": "'{{ _(\\'health_api_params\\') }}'",
    "'Ресурси Системи'": "'{{ _(\\'health_sys_resources\\') }}'",
    ">Закрити<": ">{{ _('health_close') }}<"
}
process_file('app/templates/health.html', health_replacements)

print("Translations applied successfully!")
