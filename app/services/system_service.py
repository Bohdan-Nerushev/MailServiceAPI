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

def get_system_info():
    """Sammelt detaillierte Informationen über die Maschine."""
    info = {}
    try:
        # OS Info
        info["os"] = subprocess.getoutput("uname -sr")
        info["hostname"] = subprocess.getoutput("hostname")
        info["hostnamectl"] = subprocess.getoutput("hostnamectl").split("\n")
        
        # Uptime
        info["uptime"] = subprocess.getoutput("uptime -p")
        
        # CPU Load
        load = subprocess.getoutput("cat /proc/loadavg").split()
        if len(load) >= 3:
            info["cpu_load"] = {"1min": load[0], "5min": load[1], "15min": load[2]}
            
        # Memory Info (in MB)
        mem = subprocess.getoutput("free -m | grep Mem").split()
        if len(mem) >= 3:
            info["memory"] = {"total": f"{mem[1]}MB", "used": f"{mem[2]}MB", "free": f"{mem[3]}MB"}
            
        # Disk Usage (Root partition)
        disk = subprocess.getoutput("df -h / | tail -1").split()
        if len(disk) >= 4:
            info["disk_usage"] = {"total": disk[1], "used": disk[2], "available": disk[3], "percent": disk[4]}
            
        # IP Addresses
        ips = subprocess.getoutput("hostname -I").split()
        info["ip_addresses"] = ips

        hostCtl = subprocess.getoutput("hostnamectl").split("\n")
        info["hostnameCTL"] = hostCtl
        
    except Exception as e:
        logger.error(f"Fehler beim Sammeln von Systeminfos: {str(e)}")
        info["error"] = str(e)
        
    return info
