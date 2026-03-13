# 📧 Mail Service API (FastAPI)

Dieses Projekt bietet eine umfassende **REST-API und Web-Oberfläche zur Verwaltung eines Mailservers**, basierend auf **Postfix**, **Dovecot** und **FastAPI**. Es enthält einen vollständigen Observability-Stack für ein produktionsbereites Monitoring.

## 🌟 Hauptfunktionen

- **Benutzerverwaltung**: Erstellen, Auflisten, Löschen von Benutzern und Passwortverwaltung.
- **E-Mail-Operationen**: Senden über SMTP, Zugriff auf Postfächer über IMAP (Abrufen, Lesen, Löschen).
- **Web-UI**: Benutzerfreundliche Oberfläche für Administration und Webmail.
- **Vollständige Observability**: Integrierte Grafana-Dashboards mit Prometheus-Metriken und Loki-Logs.
- **Sicherheit**: Integrierter SpamAssassin und automatisierte SSL/TLS-Konfiguration.
- **Ressourcen-Monitoring**: Echtzeit-Status der Systemressourcen und Mail-Dienste.

---

## 🏗 Systemarchitektur

Das System besteht aus mehreren integrierten Schichten:

1.  **Kern-Dienste**: Postfix (SMTP), Dovecot (IMAP/POP3), SpamAssassin (Antispam).
2.  **API-Schicht**: FastAPI-Anwendung, die mit Gunicorn/Uvicorn läuft.
3.  **Proxy-Schicht**: Nginx als Reverse Proxy und Metriken-Lieferant.
4.  **Monitoring-Stack (Dockerized)**:
    - **Prometheus**: Metriken-Sammlung.
    - **Loki**: Log-Aggregation.
    - **Grafana**: Visualisierungs-Dashboard.
    - **Grafana Alloy**: Einheitlicher Telemetrie-Kollektor.
    - **Exporters**: Node Exporter, cAdvisor, Nginx/Postfix/Dovecot Exporter.

---

## 🚀 Installation und Setup

### 1. Automatisierte Installation (Empfohlen für Linux)

Dieses Skript installiert alle Systemabhängigkeiten, konfiguriert Postfix/Dovecot und richtet den API-Dienst ein.

```bash
wget -O install_server.sh https://raw.githubusercontent.com/Bohdan-Nerushev/MailServiceAPI/main/install_server.sh
chmod +x install_server.sh
sudo ./install_server.sh
```

**Was das Skript ausführt:**
- Installation von Python 3.12, Nginx, Postfix, Dovecot, SpamAssassin.
- Konfiguration der Firewall (UFW) und SSL-Zertifikate.
- Einrichtung der FastAPI-Anwendung als Systemd-Dienst (`mail-api.service`).
- Konfiguration von Nginx als Reverse Proxy für die API und das Monitoring.

### 2. Monitoring-Stack bereitstellen

Die Monitoring-Suite läuft in Docker-Containern:

```bash
docker-compose up -d
```

Zugriff auf **Grafana**: `http://ihre-server-ip/monitoring/` (Standard-Login: `admin` / `admin`).

---

## ⚙️ Konfiguration (.env)

| Variable | Beschreibung | Standardwert |
|----------|-------------|--------------|
| `DOMAIN` | Ihre Server-Domain oder IP | `localhost` |
| `SMTP_SERVER` | SMTP-Server Host | `localhost` |
| `SMTP_PORT` | SMTP-Server Port | `587` |
| `IMAP_SERVER` | IMAP-Server Host | `localhost` |
| `IMAP_PORT` | IMAP-Server Port | `143` |
| `APP_PORT` | Port der FastAPI-Anwendung | `8090` |
| `DEBUG` | Debug-Modus aktivieren | `False` |
| `SUDO_USER_PASSWORD` | Passwort für die Systembenutzer-Verwaltung | *Erforderlich* |
| `DISPLAY_TIMEZONE` | Zeitzone für die Protokollierung | `Europe/Berlin` |

---

## 🌐 API & UI Endpunkte

### Dokumentation
- **Swagger UI**: `http://ihre-server-ip/docs`
- **ReDoc**: `http://ihre-server-ip/redoc`

### API Übersicht

| Kategorie | Methode | Endpunkt | Beschreibung | Auth/Header |
|-----------|---------|---------|--------------|-------------|
| **System** | GET | `/health` | Status von System & Diensten | - |
| **Benutzer** | GET | `/users/` | Alle Systembenutzer auflisten | - |
| **Benutzer** | POST | `/users/` | Neuen Mail-Benutzer anlegen | JSON Body |
| **Benutzer** | PUT | `/users/{u}/password` | Passwort ändern | JSON Body |
| **Benutzer** | DELETE | `/users/{u}` | Benutzer & Postfach löschen | `X-User-Password` Header |
| **E-Mail** | POST | `/mail/send` | E-Mail über SMTP senden | JSON Body |
| **E-Mail** | GET | `/mail/inbox/{u}` | Neueste E-Mails abrufen | `x-password` Header |
| **E-Mail** | GET | `/mail/message/{uid}` | Vollständigen Inhalt abrufen | `x-password` Header |

---

## 📊 Observability & Monitoring

### Grafana Dashboards
- **System-Metriken**: Node Exporter (ID: `1860`).
- **Container-Metriken**: cAdvisor (ID: `14282`).
- **Nginx-Status**: Nginx Exporter (ID: `11199`).
- **API-Performance**: FastAPI Instrumentator (ID: `16110`).
- **Mail-Logs**: Zugriff über Loki (`{job="fastapi"}` oder `{job="docker_logs"}`).

### Metriken-Endpunkt
Die API stellt Prometheus-kompatible Metriken unter `/metrics` bereit.

---

## 🛠 Wartung und Fehlerbehebung

### Dienst-Status prüfen
```bash
# Status aller wichtigen Dienste auf einmal prüfen
sudo systemctl status mail-api postfix dovecot nginx
```

### 📋 Protokolle (Logs & Fehlerbehebung)

#### 1. API-Dienst (mail-api)
```bash
# Echtzeit-Logs des Systemd-Dienstes
sudo journalctl -u mail-api -f

# Logs aus der Datei (falls konfiguriert)
tail -f app.log
```

#### 2. Mailserver (Postfix & Dovecot)
```bash
# SMTP- und IMAP-Ereignisse (System-Mail-Log)
sudo tail -f /var/log/mail.log

# Dienst-spezifische Journals
sudo journalctl -u postfix -f
sudo journalctl -u dovecot -f
```

#### 3. Webserver (Nginx)
```bash
# Zugriffs-Protokolle (Access Logs)
sudo tail -f /var/log/nginx/access.log

# Fehlersuche (Error Logs)
sudo tail -f /var/log/nginx/error.log
```

#### 4. Monitoring-Stack (Docker)
```bash
# Logs aller Docker-Container des Stacks
docker-compose logs -f
```

### 📈 Visualisierung in Grafana (Loki)
Für eine konsolidierte Ansicht nutzen Sie **Grafana Explore**:
1. Öffnen Sie `http://ihre-server-ip/monitoring/`.
2. Gehen Sie zum Bereich **Explore**.
3. Wählen Sie **Loki** als Datenquelle.
4. Filter nutzen: `{job="fastapi"}` oder `{job="docker_logs"}`.

### Schneller System-Check
```bash
# Aktuelle Systemauslastung (CPU, RAM, Prozesse)
top
```

### Konfiguration validieren
```bash
postconf -n                     # Postfix-Konfiguration prüfen
doveconf -n                     # Dovecot-Konfiguration prüfen
nginx -t                        # Nginx-Syntax validieren
```

---

## 🧪 Entwicklung

### Lokal ausführen
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
source venv/bin/activate
uvicorn app.main:app --reload --port 8090
```

### Tests ausführen
```bash
python3 tests/run_all.py
```