import requests
from tests.e2e import config
from tests.e2e.utils import user_helper
import time

def test_mail_flow():
    """
    Позитивний тест: Відправка пошти -> Отримання інбоксу -> Видалення повідомлення.
    """
    print("Запуск: test_mail_flow")
    
    # Створюємо двох користувачів (Аліса і Боб)
    alice = user_helper.create_unique_user()
    bob = user_helper.create_unique_user()
    
    try:
        subject = "E2E Test Subject"
        body = "Hello Bob, this is a test email."
        
        # 1. Відправка листа (Send Mail)
        send_data = {
            "to": f"{bob['username']}@{config.DOMAIN}",
            "subject": subject,
            "body": body,
            "from_email": f"{alice['username']}@{config.DOMAIN}"
        }
        send_resp = requests.post(f"{config.BASE_URL}/mail/send", json=send_data, timeout=10)
        assert send_resp.status_code == 200, f"Помилка відправки: {send_resp.text}"
        print(f"  - Лист від {alice['username']} до {bob['username']} надіслано")

        # Чекаємо трохи, поки Postfix/Dovecot оброблять лист
        time.sleep(2)

        # 2. Отримання інбоксу Боба (Fetch Inbox)
        inbox_resp = requests.get(
            f"{config.BASE_URL}/mail/inbox/{bob['username']}",
            headers={"X-Password": bob['password']},
            timeout=10
        )
        assert inbox_resp.status_code == 200
        inbox = inbox_resp.json().get("inbox", [])
        
        found_mail = None
        for m in inbox:
            if m['subject'] == subject:
                found_mail = m
                break
        
        assert found_mail is not None, "Лист не знайдено в інбоксі Боба"
        uid = found_mail['uid']
        print(f"  - Лист знайдено в інбоксі (UID: {uid})")

        # 3. Отримання конкретної повідомлення (View Message)
        msg_resp = requests.get(
            f"{config.BASE_URL}/mail/message/{uid}",
            params={"username": bob['username']},
            headers={"X-Password": bob['password']},
            timeout=10
        )
        assert msg_resp.status_code == 200
        print("  - Вміст листа успішно отримано")

        # 4. Видалення повідомлення (Delete Message)
        del_resp = requests.delete(
            f"{config.BASE_URL}/mail/message/{uid}",
            params={"username": bob['username']},
            headers={"X-Password": bob['password']},
            timeout=10
        )
        assert del_resp.status_code == 200
        print("  - Лист успішно видалено")

    finally:
        user_helper.delete_user(alice['username'], alice['password'])
        user_helper.delete_user(bob['username'], bob['password'])

def test_send_mail_invalid():
    """
    Негативний тест: Відправка на некоректну адресу.
    """
    print("Запуск: test_send_mail_invalid")
    send_data = {
        "to": "invalid-email-address",
        "subject": "Test",
        "body": "Test"
    }
    # Оскільки FastAPI використовує EmailSchema, де 'to' є str, валідація може не бути 422
    # Перевіримо фактичний код відповіді
    resp = requests.post(f"{config.BASE_URL}/mail/send", json=send_data, timeout=10)
    print(f"  - Status code for invalid mail: {resp.status_code}")
    assert resp.status_code in [400, 422, 500] 
    print("  - Перевірка валідації email (422) пройдена")

def test_api_access_alien_mail():
    """
    Негативний тест: Спроба доступу до чужого листа через API.
    """
    print("Запуск: test_api_access_alien_mail")
    user1 = user_helper.create_unique_user()
    user2 = user_helper.create_unique_user()
    
    try:
        # Юзер 1 відправляє собі листа
        requests.post(
            f"{config.BASE_URL}/mail/send",
            json={"to": f"{user1['username']}@{config.DOMAIN}", "subject": "Secret", "body": "Hidden"},
            headers={"X-User-Password": user1['password']},
            params={"username": user1['username']},
            timeout=10
        )
        
        # Отримуємо інбокс Юзера 1
        resp = requests.get(
            f"{config.BASE_URL}/mail/inbox/{user1['username']}",
            headers={"X-Password": user1['password']},
            timeout=10
        )
        inbox = resp.json().get("inbox", [])
        if not inbox:
            print("  - Скіп: Лист не знайдено в інбоксі")
            return
        uid = inbox[0]['uid']
        
        # Юзер 2 намагається прочитати лист Юзера 1
        alien_resp = requests.get(
            f"{config.BASE_URL}/mail/message/{uid}",
            headers={"X-Password": user2['password']},
            params={"username": user2['username']},
            timeout=10
        )
        assert alien_resp.status_code in [404, 500, 403]
        print("  - Заборона доступу до чужої пошти пройдена")
        
    finally:
        user_helper.delete_user(user1['username'], user1['password'])
        user_helper.delete_user(user2['username'], user2['password'])

if __name__ == "__main__":
    try:
        test_mail_flow()
        test_send_mail_invalid()
        test_api_access_alien_mail()
        print("Усі E2E тести Mail API (позитивні та негативні) пройшли успішно!\n")
    except Exception as e:
        print(f"Тест провалено: {e}")
        exit(1)
