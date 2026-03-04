import subprocess
import logging

# Einstellen Logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command: list):
    """Helper function to execute system commands via sudo."""
    try:
        # Add sudo to each command
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
    """Erstellen Sie ein Systembenutzerkonto Linux ohne Shell-Zugriff (für die E-Mail)."""
    # -m: erstellt die Home-Verzeichnis
    # -s /usr/sbin/nologin: verhindert den Zugriff auf die Shell (Sicherheit)
    success, msg = run_command(["useradd", "-m", "-s", "/usr/sbin/nologin", username])
    if not success:
        return False, msg
    
    # Passwort setzen
    return change_user_password(username, password)

def delete_system_user(username: str):
    """Delete the user and their home directory."""
    # -r: delete the home directory along with the user
    return run_command(["userdel", "-r", username])

def change_user_password(username: str, password: str):
    """Change the password of an existing user."""
    try:
        # For chpasswd we pass "user:pass" to stdin
        full_command = ["sudo", "chpasswd"]
        input_data = f"{username}:{password}"
        
        result = subprocess.run(
            full_command,
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Password for {username} successfully changed")
        return True, "Password changed"
    except subprocess.CalledProcessError as e:
        logger.error(f"Error changing password for {username}: {e.stderr}")
        return False, e.stderr

def list_system_users():
    """Return a list of all real system users (UID >= 1000)."""
    try:
        users = []
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) > 2:
                    uid = int(parts[2])
                    # UID >= 1000 — das ist normalerweise erstellte Benutzer, < 65534 (nobody)
                    if 1000 <= uid < 65534:
                        users.append(parts[0])
        return True, users
    except Exception as e:
        logger.error(f"Error getting list of users: {str(e)}")
        return False, str(e)
