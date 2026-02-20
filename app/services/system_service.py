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

def get_service_details(service_name: str) -> dict:
    """Sammelt detaillierte Status- und Konfigurationsinformationen für einen Dienst."""
    details = {
        "is_active": False,
        "config": []
    }
    try:
        active_res = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True
        )
        details["is_active"] = (active_res.stdout.strip() == "active")

        show_res = subprocess.run(
            ["systemctl", "show", service_name, "--no-page", "-p", "ActiveState,SubState,ActiveEnterTimestamp,MainPID"],
            capture_output=True,
            text=True
        )
        for line in show_res.stdout.splitlines():
            if "=" in line:
                key, val = line.split("=", 1)
                details[key] = val

        if service_name == "postfix":
            config_res = subprocess.run(["postconf", "-n"], capture_output=True, text=True)
            details["config"] = [line for line in config_res.stdout.splitlines() if line.strip()]
        elif service_name == "dovecot":
            config_res = subprocess.run(["doveconf", "-n"], capture_output=True, text=True)
            details["config"] = [line for line in config_res.stdout.splitlines() if line.strip()]

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Details für {service_name}: {str(e)}")
        details["error"] = str(e)

    return details

def get_network_info() -> dict:
    """Sammelt Informationen über die Netzwerkkonfiguration und Firewall."""
    info = {}
    try:
        # IP Routing-Tabelle
        route_res = subprocess.run(["ip", "route"], capture_output=True, text=True)
        info["routing"] = route_res.stdout.splitlines()

        # Netzwerkschnittstellen (Interfaces)
        addr_res = subprocess.run(["ip", "-brief", "address"], capture_output=True, text=True)
        info["interfaces"] = addr_res.stdout.splitlines()

        # Firewall Status (UFW)
        # Hinweis: Ohne sudo-Rechte könnte dies eingeschränkt sein
        ufw_res = subprocess.run(["ufw", "status"], capture_output=True, text=True)
        if ufw_res.returncode == 0:
            info["firewall"] = ufw_res.stdout.splitlines()
        else:
            info["firewall"] = ["Fehlende Berechtigungen (sudo) für UFW oder UFW nicht installiert.", ufw_res.stderr.strip()]
            
        # Aktive Ports (Listening)
        ss_res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True)
        # Filtere nur die ersten 15 Zeilen, um die Antwort nicht zu groß zu machen
        info["listening_ports"] = ss_res.stdout.splitlines()[:15]

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Netzwerk-Infos: {str(e)}")
        info["error"] = str(e)

    return info
