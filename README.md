# 📧 Mail Service API (FastAPI)

Dieses Projekt stellt eine **REST-API zur Verwaltung eines Mailservers** bereit, der auf **Postfix** und **Dovecot** basiert.  

Das System ermöglicht:

- Erstellen und Verwalten von Benutzern  
- Ändern von Passwörtern  
- Senden und Empfangen von E-Mails über eine **API** oder eine **Weboberfläche**

Die Lösung ist auf die **Automatisierung der Mailserver-Administration** und die **Integration mit anderen Diensten** ausgelegt.

## Architektur

Die Architektur umfasst:

- SMTP-Server
- IMAP-Server
- Spam-Filter-System
- API-Schicht für den programmgesteuerten Zugriff auf Mailfunktionen

---

# 🚀 Installation und Start

## 1. Schnelle Installation über Docker (empfohlen)

Dies ist der einfachste Weg, den Server bereitzustellen.  
Das Skript installiert automatisch Abhängigkeiten, konfiguriert Maildienste und startet die API.

### Konfiguration herunterladen

```bash
wget -O install_server.sh https://raw.githubusercontent.com/Bohdan-Nerushev/MailServiceAPI/main/install_server.sh
```

### Installationsskript bearbeiten

Öffnen Sie das Skript und geben Sie die erforderlichen Parameter für `.env` an.

### Installation starten

```bash
chmod +x install_server.sh
sudo ./install_server.sh
```

### Was das Skript ausführt

- Installation der erforderlichen Systempakete
- Konfiguration von **Postfix** und **Dovecot**
- Konfiguration der **Anti-Spam-Dienste**
- Start der Container über **Docker Compose**
- Start des **API-Dienstes**

Diese Variante ist optimal für **Production-Umgebungen**.

---

# 2️⃣ Manuelle Installation (ohne Docker)

## Repository klonen

```bash
git clone https://github.com/Bohdan-Nerushev/MailServiceAPI.git
cd MailServiceAPI
```

## Vorbereitung der Python-Umgebung

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

---

# 3️⃣ Konfiguration der Umgebungsvariablen

Erstellen Sie die Datei `.env`.

```bash
nano .env
```

Geben Sie die erforderlichen Konfigurationsparameter an.

---

# ▶️ Anwendung starten

## Entwicklungsmodus

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd) && source venv/bin/activate && python3 app/main.py
```

oder über **Uvicorn**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

---

## Production-Modus

Für einen stabilen Betrieb in Production wird **Gunicorn mit Uvicorn-Workers** verwendet.

```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)

venv/bin/gunicorn app.main:app \
--workers 4 \
--worker-class uvicorn.workers.UvicornWorker \
--bind 0.0.0.0:8090 \
--daemon
```

---

## Anwendung neu starten

```bash
sudo systemctl restart mail-api
```

## Logs anzeigen

```bash
tail -f app.log
```

---

## Tests ausführen

```bash
python3 tests/run_all.py
```

---

# 🌐 Endpoints (API und UI)

## API Endpoints (REST JSON)

### System

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| GET | `/health` | Überprüfung des Systemstatus |

### Users

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| GET | `/users/` | Liste aller Benutzer |
| POST | `/users/` | Neuen Benutzer erstellen |
| PUT | `/users/{username}/password` | Benutzerpasswort ändern |
| DELETE | `/users/{username}` | Benutzer und Postfach löschen |

### Mail

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| POST | `/mail/send` | E-Mail über SMTP senden |
| GET | `/mail/inbox/{username}` | Liste der E-Mails abrufen |
| GET | `/mail/message/{uid}` | Vollständige Nachricht abrufen |
| DELETE | `/mail/message/{uid}` | E-Mail dauerhaft löschen |

---

# UI Endpoints (Weboberfläche)

## General & Auth

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| GET | `/ui/` | Hauptseite |
| GET / POST | `/ui/login` | Login |
| GET / POST | `/ui/register` | Registrierung |
| GET / POST | `/ui/change-password` | Passwort ändern |
| GET / POST | `/ui/delete-user` | Konto löschen |
| POST | `/ui/logout` | Logout |

---

## Mailbox (Webmail)

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| GET | `/ui/inbox` | Postfachseite |
| GET / POST | `/ui/compose` | Neue E-Mail erstellen |
| GET | `/ui/mail/{uid}` | Einzelne Nachricht anzeigen |
| POST | `/ui/mail/{uid}/delete` | In Papierkorb verschieben |
| POST | `/ui/mail/{uid}/restore` | Wiederherstellen |
| POST | `/ui/mail/{uid}/permanent-delete` | Dauerhaft löschen |

---

## System Dashboard

| Methode | Endpoint | Beschreibung |
|-------|-------|-------|
| GET | `/ui/health` | Dashboard mit Status aller Dienste |
| GET | `/ui/users` | Liste aller Benutzer |

---

# 🛠 Technologie-Stack

## Backend

- **Python 3.10+**
- **FastAPI**
- **Uvicorn / Gunicorn**
- **Pydantic**
- **Prometheus FastAPI Instrumentator**
- **python-dotenv / PyYAML**

---

## Mail-Verarbeitung

- **imap-tools** — IMAP-Integration  
- **aiosmtplib** — asynchrones SMTP  
- **email-validator** — Validierung von E-Mail-Adressen  

---

## Systemmonitoring

- **psutil** — CPU / RAM / Disk Monitoring

---

## Weboberfläche

- **Jinja2** — HTML-Templates  
- **Vanilla CSS** — Styling  

---

## Mail-Infrastruktur

- **Postfix** — SMTP-Server  
- **Dovecot** — IMAP / POP3  
- **SpamAssassin** — Spamfilter  
- **Procmail** — Mailzustellung  
- **Nginx** — Reverse Proxy und Monitoring

---

# ⚙️ Anzeigen der Service-Konfigurationen

Dieser Abschnitt enthält Befehle zur Überprüfung der aktuellen Konfiguration wichtiger Dienste.

---

# 🐘 Postfix

Nur aktive Einstellungen anzeigen:

```bash
postconf -n
```

Alle Einstellungen anzeigen:

```bash
postconf
```

---

# 🕊️ Dovecot

Aktive Konfiguration anzeigen:

```bash
doveconf -n
```

Alle Einstellungen anzeigen:

```bash
doveconf
```

---

# 🌐 Nginx

Syntax prüfen:

```bash
nginx -t
```

Site-Konfiguration anzeigen:

```bash
cat /etc/nginx/sites-enabled/mailservice
```

Gesamte Konfiguration anzeigen:

```bash
nginx -T
```

---

# 📨 Procmail

Globale Regeln anzeigen:

```bash
cat /etc/procmailrc
```

Benutzerregeln anzeigen:

```bash
cat ~/.procmailrc
```

---

# 🛡️ SpamAssassin

Konfiguration prüfen:

```bash
spamassassin --lint
```

Konfigurationsdatei anzeigen:

```bash
cat /etc/spamassassin/local.cf
```