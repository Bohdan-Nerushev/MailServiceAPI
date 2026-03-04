# 📧 Mail Service API (FastAPI)

Dieser Dienst bietet eine REST-API zur Verwaltung eines Mailservers (Postfix/Dovecot).

---

## 🚀 Projektstart

### 1. Vorbereitung (einmalig)
Stellen Sie sicher, dass Sie sich im Projektverzeichnis befinden:
```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv
# Aktivierung
source venv/bin/activate
# Abhängigkeiten installieren
pip install -r requirements.txt
```

### 2. Anwendung starten
Verwenden Sie diesen Befehl, um den Server zu starten:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd) && source venv/bin/activate && python3 app/main.py
```

Alternativ direkt mit Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090 
```

---

## 🛠 API-Endpunkte

### E-Mail-Verwaltung (`/mail`)
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **POST** | `/mail/send` | Versendet eine E-Mail über SMTP. |
| **GET** | `/mail/inbox/{username}` | Listet E-Mails im Posteingang auf. |
| **GET** | `/mail/message/{uid}` | Ruft den Inhalt einer spezifischen E-Mail ab. |
| **DELETE**| `/mail/message/{uid}` | Löscht eine E-Mail dauerhaft. |

**Beispiel: E-Mail senden**
```bash
curl -X POST http://localhost:8090/mail/send \
     -H "Content-Type: application/json" \
     -d '{
       "to": "empfaenger@beispiel.de",
       "subject": "Test-Betreff",
       "body": "Hallo, das ist eine Test-E-Mail.",
       "from_email": "sender@lehrwerkstatt.local"
     }'
```

**Beispiel: Posteingang abrufen**
```bash
curl -X GET http://localhost:8090/mail/inbox/testuser \
     -H "x-password: MeinSicheresPasswort"
```

### System & Health (`/`)
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/` | Basis-Endpoint mit Status-Nachricht. |
| **GET** | `/health` | Detaillierte Prüfung des Systemstatus. |

### Benutzerverwaltung (`/users`)
| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| **GET** | `/users/` | Listet alle Systembenutzer auf. |
| **POST** | `/users/` | Erstellt einen neuen E-Mail-Benutzer. |
| **PUT** | `/users/{username}/password` | Ändert das Passwort eines Benutzers. |
| **DELETE**| `/users/{username}` | Löscht einen Benutzer. |

**Beispiel: Benutzer erstellen**
```bash
curl -X POST http://localhost:8090/users/ \
     -H "Content-Type: application/json" \
     -d '{
       "username": "neuer_benutzer",
       "password": "SehrSicheresPasswort123!"
     }'
```

**Beispiel: Passwort ändern**
```bash
curl -X PUT http://localhost:8090/users/neuer_benutzer/password \
     -H "Content-Type: application/json" \
     -d '{
       "current_password": "SehrSicheresPasswort123!",
       "new_password": "NochSichereresPasswort456!"
     }'
```

---

## 🔗 Service-Adressen

Nach dem Start ist die API unter folgenden Adressen erreichbar:

| Dienst | Adresse |
| :--- | :--- |
| **API Root** | [http://localhost:8090](http://localhost:8090) |
| **Swagger UI (Dokumentation)** | [http://localhost:8090/docs](http://localhost:8090/docs) |
| **Redocly** | [http://localhost:8090/redoc](http://localhost:8090/redoc) |

---

## 📝 Protokollierung (Logging)
Alle Aktionen (Benutzererstellung, Senden und Empfangen von E-Mails) werden in der Datei `app.log` im Stammverzeichnis protokolliert.

