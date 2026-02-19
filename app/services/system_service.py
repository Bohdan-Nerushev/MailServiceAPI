import subprocess
import logging

logger = logging.getLogger(__name__)

def get_service_status(service_name: str) -> bool:
    """Überprüft, ob ein Systemd-Dienst aktiv ist."""
    try:
        # 'is-active' gibt 'active' zurück, wenn der Dienst läuft
        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() == "active"
    except Exception as e:
        logger.error(f"Fehler beim Überprüfen des Dienstes {service_name}: {str(e)}")
        return False
