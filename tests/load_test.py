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
    print("START DES LASTTESTS (LOAD TEST)")
    print(f"Benutzer: {num_users}, Runden: {rounds}")
    print("========================================\n")

    users = []
    
    try:
        # 1. Erstellung des Benutzer-Pools
        print(f"--> Erstellung von {num_users} Testbenutzern...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_user = {executor.submit(user_helper.create_unique_user): i for i in range(num_users)}
            for future in concurrent.futures.as_completed(future_to_user):
                try:
                    user = future.result()
                    users.append(user)
                    print(f"    Benutzer {user['username']} erstellt.")
                except Exception as e:
                    print(f"    Fehler bei der Erstellung: {e}")

        if len(users) < 2:
            print("!!! Nicht genügend Benutzer für den Test.")
            return

        # 2. Senden von Nachrichten
        print(f"\n--> Start des E-Mail-Versands ({rounds} Runden)...")
        
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
                    print(f"    [!] Fehler beim Senden von {sender['username']}: {resp.status_code}")
                    return False
            except Exception as e:
                print(f"    [!] Exception beim Senden: {e}")
                return False

        for round_idx in range(1, rounds + 1):
            print(f"    Runde {round_idx}...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(send_random_mail, users))
                success_count = sum(1 for r in results if r)
                print(f"    Runde {round_idx} abgeschlossen: {success_count}/{len(users)} erfolgreich.")

        print("\n--> Lasttest des Versands abgeschlossen.")

    except Exception as e:
        print(f"!!! Fehler während des Lasttests: {e}")
    
    finally:
        # 3. Bereinigung
        print(f"\n--> Löschen von {len(users)} Testbenutzern...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            for user in users:
                executor.submit(user_helper.delete_user, user['username'], user['password'])
        print("--> Bereinigung abgeschlossen.")
        print("========================================\n")

if __name__ == "__main__":
    run_load_test()
