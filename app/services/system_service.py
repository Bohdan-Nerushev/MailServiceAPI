import os
import subprocess
import logging

logger = logging.getLogger(__name__)

import tempfile
import stat

def run_sudo_command(command: list, input_data: str = None) -> subprocess.CompletedProcess:
    """Executes a command with sudo -A using a temporary askpass script."""
    sudo_password = os.getenv("SUDO_USER_PASSWORD", "")
    
    if not sudo_password:
        logger.warning("SUDO_USER_PASSWORD not found in environment. Trying sudo -n.")
        return subprocess.run(
            ["sudo", "-n"] + command,
            input=input_data,
            capture_output=True,
            text=True
        )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(f"#!/bin/sh\necho '{sudo_password}'\n")
        askpass_path = f.name
    
    try:
        os.chmod(askpass_path, os.stat(askpass_path).st_mode | stat.S_IEXEC)
        env = os.environ.copy()
        env['SUDO_ASKPASS'] = askpass_path
        
        return subprocess.run(
            ["sudo", "-A"] + command,
            input=input_data,
            capture_output=True,
            text=True,
            env=env
        )
    finally:
        if os.path.exists(askpass_path):
            os.remove(askpass_path)

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

import psutil

def get_hostnamectl() -> list:
    """Returns detailed information from hostnamectl command."""
    try:
        res = subprocess.run(["hostnamectl"], capture_output=True, text=True)
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return ["hostnamectl not available"]

def get_system_info():
    """Sammelt detaillierte Informationen über die Maschine."""
    info = {}
    try:
        # OS Info
        info["os"] = subprocess.getoutput("uname -sr")
        info["hostname"] = subprocess.getoutput("hostname")
        info["hostnamectl"] = get_hostnamectl()
        
        # Uptime
        info["uptime"] = subprocess.getoutput("uptime -p")
        
        # CPU
        info["cpu"] = {
            "percent": psutil.cpu_percent(interval=None),
            "count": psutil.cpu_count(),
            "load_1min": os.getloadavg()[0]
        }
            
        # Memory
        mem = psutil.virtual_memory()
        info["memory"] = {
            "total": f"{mem.total // (1024**2)}MB",
            "used": f"{mem.used // (1024**2)}MB", 
            "free": f"{mem.available // (1024**2)}MB",
            "percent": mem.percent
        }
            
        # Disk
        disk = psutil.disk_usage('/')
        info["disk_usage"] = {
            "total": f"{disk.total // (1024**3)}GB",
            "used": f"{disk.used // (1024**3)}GB",
            "available": f"{disk.free // (1024**3)}GB",
            "percent": f"{disk.percent}%"
        }
            
        # IP Addresses
        info["ip_addresses"] = subprocess.getoutput("hostname -I").split()
        
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
    info = {"interfaces": [], "firewall": [], "listening_ports": []}
    try:
        # Structured Interfaces via psutil
        for name, addrs in psutil.net_if_addrs().items():
            if_info = {"name": name, "addresses": []}
            for addr in addrs:
                if_info["addresses"].append({
                    "family": str(addr.family),
                    "addr": addr.address,
                    "netmask": addr.netmask
                })
            info["interfaces"].append(if_info)

        # Firewall Status (UFW)
        ufw_res = run_sudo_command(["ufw", "status"])
        if ufw_res.returncode == 0:
            info["firewall"] = ufw_res.stdout.splitlines()
        else:
            info["firewall"] = ["Permission Error or UFW not installed"]
            
        # Listening Ports
        ss_res = subprocess.run(["ss", "-tulpn"], capture_output=True, text=True)
        info["listening_ports"] = ss_res.stdout.splitlines()[:15]

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Netzwerk-Infos: {str(e)}")
        info["error"] = str(e)

    return info


def get_mail_security_status() -> dict:
    """Sammelt Informationen über SpamAssassin, Procmail und die Postfix-Integration."""
    status = {
        "spamassassin": {
            "service": "unknown",
            "is_active": False,
            "spamd_version": "unknown"
        },
        "procmail": {
            "installed": False,
            "global_config_exists": False
        },
        "postfix_integration": {
            "content_filter_enabled": False,
            "filter_service_defined": False
        }
    }

    try:
        # SpamAssassin Service Status
        spamd_res = subprocess.run(["systemctl", "is-active", "spamd"], capture_output=True, text=True)
        status["spamassassin"]["service"] = spamd_res.stdout.strip()
        status["spamassassin"]["is_active"] = (status["spamassassin"]["service"] == "active")

        # SpamAssassin Version
        version_res = subprocess.run(["spamassassin", "-V"], capture_output=True, text=True)
        if version_res.returncode == 0:
            status["spamassassin"]["spamd_version"] = version_res.stdout.splitlines()[0]

        # Procmail Status
        status["procmail"]["installed"] = os.path.exists("/usr/bin/procmail")
        status["procmail"]["global_config_exists"] = os.path.exists("/etc/procmailrc")

        # Postfix Integration Check
        master_cf_res = run_sudo_command(["grep", "-E", "content_filter=spamassassin", "/etc/postfix/master.cf"])
        status["postfix_integration"]["content_filter_enabled"] = (master_cf_res.returncode == 0)

        master_cf_service_res = run_sudo_command(["grep", "^spamassassin", "/etc/postfix/master.cf"])
        status["postfix_integration"]["filter_service_defined"] = (master_cf_service_res.returncode == 0)

    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Mail-Security-Infos: {str(e)}")
        status["error"] = str(e)

    return status
