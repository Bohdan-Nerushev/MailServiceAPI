import requests
from tests.e2e import config
from tests.e2e.utils import user_helper, auth_helper
import time

def test_ui_mail_cycle():
    """
    Позитивний тест UI: Compose -> Send -> Inbox -> Trash -> Restore -> Permanent Delete.
    """
    print("Запуск: test_ui_mail_cycle (повний цикл)")
    
    user = user_helper.create_unique_user()
    session = auth_helper.get_ui_session(user['username'], user['password'])
    
    try:
        # 1. Відправка листа (UI Compose)
        subject = f"UI Trash Test {int(time.time())}"
        session.post(
            f"{config.BASE_URL}/ui/compose",
            data={"to": f"{user['username']}@{config.DOMAIN}", "subject": subject, "body": "Test Trash Flow"},
            timeout=10
        )
        time.sleep(1)

        # 2. Пошук листа в Inbox та отримання UID
        inbox_resp = session.get(f"{config.BASE_URL}/ui/inbox", timeout=10)
        # У вашому UI UID зазвичай передається в посиланнях або формах. 
        # Спробуємо розпарсити UID з посилання /ui/mail/{uid}
        import re
        match = re.search(r'/ui/mail/(\d+)', inbox_resp.text)
        assert match, "Не вдалося знайти UID листа в інбоксі через UI"
        uid = match.group(1)
        print(f"  - Лист знайдено, UID: {uid}")

        # 3. Переміщення в кошик (Move to Trash)
        del_resp = session.post(f"{config.BASE_URL}/ui/mail/{uid}/delete", data={"folder": "INBOX"}, allow_redirects=True, timeout=10)
        if del_resp.status_code != 200:
            print(f"  - ERROR: Status {del_resp.status_code}, Response: {del_resp.text[:500]}")
        assert del_resp.status_code == 200
        print("  - Лист переміщено в кошик")

        # 4. Перевірка в папці Trash
        trash_resp = session.get(f"{config.BASE_URL}/ui/inbox", params={"folder": "Trash"}, timeout=10)
        assert subject in trash_resp.text
        print("  - Лист підтверджено в папці Trash")

        # 5. Відновлення з кошика (Restore)
        restore_resp = session.post(f"{config.BASE_URL}/ui/mail/{uid}/restore", allow_redirects=True, timeout=10)
        assert restore_resp.status_code == 200
        
        inbox_again = session.get(f"{config.BASE_URL}/ui/inbox", timeout=10)
        assert subject in inbox_again.text
        print("  - Лист успішно відновлено в INBOX")

        # 6. Остаточне видалення (Permanent Delete)
        # Спочатку знову в кошик
        session.post(f"{config.BASE_URL}/ui/mail/{uid}/delete", data={"folder": "INBOX"}, timeout=10)
        perm_del_resp = session.post(f"{config.BASE_URL}/ui/mail/{uid}/permanent-delete", allow_redirects=True, timeout=10)
        assert perm_del_resp.status_code == 200
        
        trash_final = session.get(f"{config.BASE_URL}/ui/inbox", params={"folder": "Trash"}, timeout=10)
        assert subject not in trash_final.text
        print("  - Лист остаточно видалено з кошика")

    finally:
        user_helper.delete_user(user['username'], user['password'])

def test_ui_compose_empty_fields():
    """
    Негативний тест UI: Спроба відправки листа з порожніми полями.
    """
    print("Запуск: test_ui_compose_empty_fields")
    user = user_helper.create_unique_user()
    session = auth_helper.get_ui_session(user['username'], user['password'])
    
    try:
        # Відправка без теми та тіла (requests не враховує HTML5 required атрибути, тому це перевірить серверну логіку)
        resp = session.post(
            f"{config.BASE_URL}/ui/compose",
            data={"to": "", "subject": "", "body": ""},
            allow_redirects=True,
            timeout=10
        )
        # Очікуємо помилку або повернення до форми
        assert "compose" in resp.url or "error" in resp.text.lower()
        print("  - Валідація порожніх полів при відправці через UI пройдена")
    finally:
        user_helper.delete_user(user['username'], user['password'])

def test_ui_cross_user_mail():
    """
    Позитивний тест UI: Alice -> Send Mail -> Bob -> Check Inbox.
    """
    print("Запуск: test_ui_cross_user_mail (User 1 -> User 2)")
    
    alice = user_helper.create_unique_user()
    bob = user_helper.create_unique_user()
    
    try:
        # 1. Alice надсилає листа Бобу
        alice_session = auth_helper.get_ui_session(alice['username'], alice['password'])
        subject = f"Cross-user Test {int(time.time())}"
        alice_session.post(
            f"{config.BASE_URL}/ui/compose",
            data={"to": f"{bob['username']}@{config.DOMAIN}", "subject": subject, "body": "Hi Bob!"},
            timeout=10
        )
        print(f"  - Alice ({alice['username']}) надіслала лист Бобу ({bob['username']})")
        time.sleep(2)

        # 2. Bob логіниться та перевіряє Inbox
        bob_session = auth_helper.get_ui_session(bob['username'], bob['password'])
        inbox_resp = bob_session.get(f"{config.BASE_URL}/ui/inbox", timeout=10)
        
        assert subject in inbox_resp.text, f"Лист з темою '{subject}' не знайдено в інбоксі Боба"
        print(f"  - Bob ({bob['username']}) отримав лист від Alice")

    finally:
        user_helper.delete_user(alice['username'], alice['password'])
        user_helper.delete_user(bob['username'], bob['password'])

if __name__ == "__main__":
    try:
        test_ui_mail_cycle()
        test_ui_compose_empty_fields()
        test_ui_cross_user_mail()
        print("Усі E2E тести Mail UI (позитивні та негативні) пройшли успішно!\n")
    except Exception as e:
        print(f"Тест провалено: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
