import os
import subprocess
import logging
import tempfile
import stat
import crypt

# Einstellen Logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _run_sudo_with_askpass(command: list, input_data: str = None, check: bool = True):
    """Executes a command with sudo -A using a temporary askpass script."""
    sudo_password = os.getenv("SUDO_USER_PASSWORD", "")
    
    if not sudo_password:
        logger.warning("SUDO_USER_PASSWORD not found in environment. Trying sudo -n.")
        return subprocess.run(
            ["sudo", "-n"] + command,
            input=input_data,
            capture_output=True,
            text=True,
            check=check
        )

    # Create a temporary script for SUDO_ASKPASS
    # We use a context manager to ensure cleanup
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        # Use single quotes for the password to avoid shell expansion issues
        f.write(f"#!/bin/sh\necho '{sudo_password}'\n")
        askpass_path = f.name
    
    try:
        # Make the script executable
        os.chmod(askpass_path, os.stat(askpass_path).st_mode | stat.S_IEXEC)
        
        env = os.environ.copy()
        env['SUDO_ASKPASS'] = askpass_path
        
        return subprocess.run(
            ["sudo", "-A"] + command,
            input=input_data,
            capture_output=True,
            text=True,
            check=check,
            env=env
        )
    finally:
        if os.path.exists(askpass_path):
            os.remove(askpass_path)

def run_command(command: list):
    """Helper function to execute system commands via sudo."""
    try:
        result = _run_sudo_with_askpass(command)
        logger.info(f"Команда виконана успішно: sudo {' '.join(command)}")
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
    pw_success, pw_msg = change_user_password(username, password)
    if not pw_success:
        # Rollback: Delete the user if password setting failed
        delete_system_user(username)
        return False, f"User created but password setting failed: {pw_msg}"
        
    return True, "User created successfully"

def delete_system_user(username: str):
    """Delete the user and their home directory."""
    # -r: delete the home directory along with the user
    return run_command(["userdel", "-r", username])

def change_user_password(username: str, password: str):
    """Change the password of an existing user."""
    try:
        # For chpasswd we pass "user:pass" to stdin
        # Now using ASKPASS, stdin is free for chpasswd
        input_data = f"{username}:{password}\n"
        
        result = _run_sudo_with_askpass(["chpasswd"], input_data=input_data)
        
        logger.info(f"Password for {username} successfully changed")
        return True, "Password changed"
    except subprocess.CalledProcessError as e:
        logger.error(f"Error changing password for {username}: {e.stderr}")
        return False, e.stderr

def list_system_users():
    """Return a list of all real system users (UID >= 1000) with details."""
    try:
        users = []
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) > 5:
                    uid = int(parts[2])
                    # UID >= 1000 — das ist normalerweise erstellte Benutzer
                    if 1000 <= uid < 65534:
                        users.append({
                            "username": parts[0],
                            "uid": parts[2],
                            "gid": parts[3],
                            "home_dir": parts[5]
                        })
        return True, users
    except Exception as e:
        logger.error(f"Error getting list of users: {str(e)}")
        return False, str(e)

def verify_user_password(username: str, password: str) -> bool:
    """Verifies a user's password by checking it against the hash in /etc/shadow."""
    try:
        # We need sudo to read /etc/shadow
        # We search for the line starting with "username:"
        command = ["grep", f"^{username}:", "/etc/shadow"]
        result = _run_sudo_with_askpass(command, check=False)
        
        if result.returncode != 0 or not result.stdout:
            logger.error(f"User {username} not found in /etc/shadow")
            return False
            
        line = result.stdout.strip()
        parts = line.split(":")
        if len(parts) < 2:
            return False
            
        stored_hash = parts[1]
        
        # crypt.crypt(password, salt) where salt is the stored hash
        # It automatically extracts the salt from the hash.
        return crypt.crypt(password, stored_hash) == stored_hash
        
    except Exception as e:
        logger.error(f"Error verifying password for {username}: {str(e)}")
        return False
