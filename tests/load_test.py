import concurrent.futures
import time
import random
import requests
from tests.e2e import config
from tests.e2e.utils import user_helper

def run_load_test(num_users=5, rounds=3):
    """
    Виконує навантажувальний тест:
    1. Створює групу тестових користувачів.
    2. Кожен користувач паралельно надсилає листи іншим користувачам.
    3. Видаляє всіх створених користувачів.
    """
    print("========================================")
    print("ЗАПУСК НАВАНТАЖУВАЛЬНОГО ТЕСТУ (LOAD TEST)")
    print(f"Користувачів: {num_users}, Раундів: {rounds}")
    print("========================================\n")

    users = []
    
    try:
        # 1. Створення пулу користувачів
        print(f"--> Створення {num_users} тестових користувачів...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_user = {executor.submit(user_helper.create_unique_user): i for i in range(num_users)}
            for future in concurrent.futures.as_completed(future_to_user):
                try:
                    user = future.result()
                    users.append(user)
                    print(f"    Користувач {user['username']} створений.")
                except Exception as e:
                    print(f"    Помилка при створенні: {e}")

        if len(users) < 2:
            print("!!! Недостатньо користувачів для тесту.")
            return

        # 2. Відправка повідомлень
        print(f"\n--> Початок відправки повідомлень ({rounds} раундів)...")
        
        def send_random_mail(sender):
            recipient = random.choice([u for u in users if u != sender])
            to_email = f"{recipient['username']}@{config.DOMAIN}"
            subject = f"Load Test Mail from {sender['username']}"
            body = f"Heavy load test content. Round {round_idx}."
            
            try:
                resp = requests.post(
                    f"{config.BASE_URL}/mail/send",
                    json={
                        "to": to_email,
                        "subject": subject,
                        "body": body,
                        "from_email": f"{sender['username']}@{config.DOMAIN}"
                    },
                    timeout=15
                )
                if resp.status_code == 200:
                    return True
                else:
                    print(f"    [!] Помилка відправки від {sender['username']}: {resp.status_code}")
                    return False
            except Exception as e:
                print(f"    [!] Exception при відправці: {e}")
                return False

        for round_idx in range(1, rounds + 1):
            print(f"    Раунд {round_idx}...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(send_random_mail, users))
                success_count = sum(1 for r in results if r)
                print(f"    Завершено раунд {round_idx}: {success_count}/{len(users)} успішно.")

        print("\n--> Навантажувальний тест відправки завершено.")

    except Exception as e:
        print(f"!!! Помилка під час лоад-тесту: {e}")
    
    finally:
        # 3. Прибирання
        print(f"\n--> Видалення {len(users)} тестових користувачів...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for user in users:
                executor.submit(user_helper.delete_user, user['username'], user['password'])
        print("--> Очищення завершено.")
        print("========================================\n")

if __name__ == "__main__":
    run_load_test()
