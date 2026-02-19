import subprocess
import logging

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command: list):
    """Допоміжна функція для виконання системних команд через sudo."""
    try:
        # Додаємо sudo до кожної команди
        full_command = ["sudo"] + command
        result = subprocess.run(
            full_command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"Команда виконана успішно: {' '.join(full_command)}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Помилка виконання команди {' '.join(e.cmd)}: {e.stderr}")
        return False, e.stderr

def create_system_user(username: str, password: str):
    """Створює системного користувача Linux без доступу до оболонки (для пошти)."""
    # -m: створити домашню директорію
    # -s /usr/sbin/nologin: заборонити вхід у термінал (безпека)
    success, msg = run_command(["useradd", "-m", "-s", "/usr/sbin/nologin", username])
    if not success:
        return False, msg
    
    # Встановлюємо пароль
    return change_user_password(username, password)

def delete_system_user(username: str):
    """Видаляє користувача та його домашню директорію."""
    # -r: видалити домашню директорію разом з юзером
    return run_command(["userdel", "-r", username])

def change_user_password(username: str, password: str):
    """Змінює пароль існуючого користувача."""
    try:
        # Для chpasswd ми передаємо "user:pass" у stdin
        full_command = ["sudo", "chpasswd"]
        input_data = f"{username}:{password}"
        
        result = subprocess.run(
            full_command,
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Пароль для {username} успішно змінено")
        return True, "Пароль змінено"
    except subprocess.CalledProcessError as e:
        logger.error(f"Помилка зміни пароля для {username}: {e.stderr}")
        return False, e.stderr

def list_system_users():
    """Повертає список усіх реальних користувачів системи (UID >= 1000)."""
    try:
        users = []
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) > 2:
                    uid = int(parts[2])
                    # UID >= 1000 — це зазвичай створені користувачі, < 65534 (nobody)
                    if 1000 <= uid < 65534:
                        users.append(parts[0])
        return True, users
    except Exception as e:
        logger.error(f"Помилка отримання списку користувачів: {str(e)}")
        return False, str(e)
