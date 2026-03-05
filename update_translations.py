import json
import sys

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

uk = load_json('app/locales/uk.json')
en = load_json('app/locales/en.json')
de = load_json('app/locales/de.json')

new_uk = {
    'reg_err_passwords_mismatch': 'Паролі не збігаються',
    'reg_success': 'Користувача {username} успішно створено! Повернення до списку...',
    'reg_err_creation': 'Помилка створення',
    'login_err_invalid': 'Невірний логін або пароль',
    'chpw_err_mismatch': 'Нові паролі не збігаються',
    'chpw_err_wrong_pass': 'Невірний поточний пароль',
    'chpw_success': 'Пароль успішно оновлено! Повернення до списку...',
    'chpw_err_update': 'Помилка оновлення',
    'del_err_confirm_word': "Будь ласка, введіть 'DELETE' для підтвердження",
    'del_err_wrong_pass': 'Невірний пароль для підтвердження видалення',
    'del_success': 'Акаунт {username} видалено назавжди. Повернення до списку...',
    'del_err_deletion': 'Помилка видалення',
    'compose_title': 'Написати нове повідомлення',
    'compose_to': 'Отримувач (E-mail)',
    'compose_subject': 'Тема листа',
    'compose_subject_placeholder': 'Заголовок повідомлення',
    'compose_body': 'Повідомлення',
    'compose_body_placeholder': 'Ваш текст тут...',
    'compose_btn_send': 'Надіслати зараз',
    'compose_success': 'Лист успішно надіслано! Повернення до вхідних...',
    'view_mail_title': 'Перегляд листа',
    'view_mail_moved_to_trash': 'Лист переміщено до кошика. Повернення...',
    'view_mail_back': 'Назад до списку',
    'view_mail_confirm_delete': 'Ви впевнені, що хочете видалити цей лист у кошик?',
    'view_mail_delete_btn': 'Видалити',
    'view_mail_unknown_sender': 'Невідомий відправник',
    'view_mail_to': 'Кому',
    'view_mail_you': 'Ви',
    'view_mail_attachments': 'Вкладення',
}

new_en = {
    'reg_err_passwords_mismatch': 'Passwords do not match',
    'reg_success': 'User {username} created successfully! Returning to list...',
    'reg_err_creation': 'Creation error',
    'login_err_invalid': 'Invalid username or password',
    'chpw_err_mismatch': 'New passwords do not match',
    'chpw_err_wrong_pass': 'Wrong current password',
    'chpw_success': 'Password updated successfully! Returning to list...',
    'chpw_err_update': 'Update error',
    'del_err_confirm_word': "Please type 'DELETE' to confirm",
    'del_err_wrong_pass': 'Wrong password for deletion confirmation',
    'del_success': 'Account {username} permanently deleted. Returning to list...',
    'del_err_deletion': 'Deletion error',
    'compose_title': 'Compose New Message',
    'compose_to': 'Recipient (E-mail)',
    'compose_subject': 'Subject',
    'compose_subject_placeholder': 'Message subject',
    'compose_body': 'Message',
    'compose_body_placeholder': 'Your text here...',
    'compose_btn_send': 'Send now',
    'compose_success': 'Email sent successfully! Returning to inbox...',
    'view_mail_title': 'View Email',
    'view_mail_moved_to_trash': 'Email moved to Trash. Returning...',
    'view_mail_back': 'Back to list',
    'view_mail_confirm_delete': 'Are you sure you want to move this email to Trash?',
    'view_mail_delete_btn': 'Delete',
    'view_mail_unknown_sender': 'Unknown sender',
    'view_mail_to': 'To',
    'view_mail_you': 'You',
    'view_mail_attachments': 'Attachments',
}

new_de = {
    'reg_err_passwords_mismatch': 'Passwoerter stimmen nicht ueberein',
    'reg_success': 'Benutzer {username} erfolgreich erstellt! Zurueck zur Liste...',
    'reg_err_creation': 'Fehler beim Erstellen',
    'login_err_invalid': 'Ungueltiger Benutzername oder Passwort',
    'chpw_err_mismatch': 'Neue Passwoerter stimmen nicht ueberein',
    'chpw_err_wrong_pass': 'Falsches aktuelles Passwort',
    'chpw_success': 'Passwort erfolgreich aktualisiert! Zurueck zur Liste...',
    'chpw_err_update': 'Aktualisierungsfehler',
    'del_err_confirm_word': "Bitte geben Sie 'DELETE' zur Bestaetigung ein",
    'del_err_wrong_pass': 'Falsches Passwort fuer die Loeschbestaetigung',
    'del_success': 'Konto {username} dauerhaft geloescht. Zurueck zur Liste...',
    'del_err_deletion': 'Loeschfehler',
    'compose_title': 'Neue Nachricht verfassen',
    'compose_to': 'Empfaenger (E-Mail)',
    'compose_subject': 'Betreff',
    'compose_subject_placeholder': 'Betreff der Nachricht',
    'compose_body': 'Nachricht',
    'compose_body_placeholder': 'Ihr Text hier...',
    'compose_btn_send': 'Jetzt senden',
    'compose_success': 'E-Mail erfolgreich gesendet! Zurueck zum Posteingang...',
    'view_mail_title': 'E-Mail anzeigen',
    'view_mail_moved_to_trash': 'E-Mail in den Papierkorb verschoben. Zurueck...',
    'view_mail_back': 'Zurueck zur Liste',
    'view_mail_confirm_delete': 'Sind Sie sicher, dass Sie diese E-Mail in den Papierkorb verschieben moechten?',
    'view_mail_delete_btn': 'Loeschen',
    'view_mail_unknown_sender': 'Unbekannter Absender',
    'view_mail_to': 'An',
    'view_mail_you': 'Sie',
    'view_mail_attachments': 'Anhaenge',
}

uk.update(new_uk)
en.update(new_en)
de.update(new_de)

save_json(uk, 'app/locales/uk.json')
save_json(en, 'app/locales/en.json')
save_json(de, 'app/locales/de.json')

print(f"uk: {len(uk)} keys, en: {len(en)} keys, de: {len(de)} keys")
sys.exit(0)
