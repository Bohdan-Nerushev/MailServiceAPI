import json, re

# Update json files
with open('app/locales/uk.json', 'r', encoding='utf-8') as f: uk = json.load(f)
with open('app/locales/en.json', 'r', encoding='utf-8') as f: en = json.load(f)
with open('app/locales/de.json', 'r', encoding='utf-8') as f: de = json.load(f)

new_keys = {
    "login_welcome": ("З поверненням", "Welcome back", "Willkommen zurück"),
    "login_subtitle": ("Увійдіть у свій поштовий акаунт", "Log in to your mail account", "Melden Sie sich an"),
    "login_select_acc": ("Оберіть акаунт", "Select account", "Konto auswählen"),
    "login_choose_user": ("Оберіть користувача...", "Choose user...", "Benutzer auswählen..."),
    "login_password": ("Пароль", "Password", "Passwort"),
    "login_btn_inbox": ("Увійти до Inbox", "Log In to Inbox", "Zum Posteingang anmelden"),
    "login_no_acc": ("Ще немає акаунту?", "Don't have an account?", "Noch kein Konto?"),
    "login_create_now": ("Створити зараз", "Create now", "Jetzt erstellen")
}

for k, (u, e, d) in new_keys.items():
    uk[k] = u
    en[k] = e
    de[k] = d

with open('app/locales/uk.json', 'w', encoding='utf-8') as f: json.dump(uk, f, ensure_ascii=False, indent=2)
with open('app/locales/en.json', 'w', encoding='utf-8') as f: json.dump(en, f, ensure_ascii=False, indent=2)
with open('app/locales/de.json', 'w', encoding='utf-8') as f: json.dump(de, f, ensure_ascii=False, indent=2)

with open('app/templates/login.html', 'r', encoding='utf-8') as f: content = f.read()

reps = {
    "З поверненням": "{{ _('login_welcome') }}",
    "Увійдіть у свій поштовий акаунт": "{{ _('login_subtitle') }}",
    "Оберіть акаунт": "{{ _('login_select_acc') }}",
    "Оберіть користувача...": "{{ _('login_choose_user') }}",
    ">Пароль<": ">{{ _('login_password') }}<",
    "Увійти до Inbox": "{{ _('login_btn_inbox') }}",
    "Ще немає акаунту?": "{{ _('login_no_acc') }}",
    "Створити зараз": "{{ _('login_create_now') }}"
}

for o, n in reps.items(): content = content.replace(o, n)

with open('app/templates/login.html', 'w', encoding='utf-8') as f: f.write(content)
print("Updated login.html")
