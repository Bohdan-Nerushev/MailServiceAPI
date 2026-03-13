#!/bin/bash
#
#Запуск як виконуваного файлу (production підхід)
#
#Спочатку додаємо execute permission:
#
#    chmod +x install_server.sh
#
#Після цього:
#
#    ./install_server.sh
#
# ==============================================================================
# Скрипт автоматичного розгортання Mail Service API та Поштового сервера
# ==============================================================================

set -euo pipefail

if [ "$EUID" -ne 0 ]; then
    echo "Run as root"
    exit 1
fi

log() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG_FILE"
}

# ==============================================================================
# БЛОК НАЛАШТУВАНЬ (Заповніть перед запуском)
# ==============================================================================
REPO_URL="https://github.com/Bohdan-Nerushev/MailServiceAPI.git"
DOMAIN_NAME="<ВСТАВТЕ_ВАШ_ДОМЕН_АБО_IP>"             
APP_DIR="/opt/mail-service-api"                       
APP_PORT="8090"                                      
APP_USER="mailapi"                           
CERT_DIR="/etc/postfix/ssl"                          
LOG_FILE="/var/log/mail_api_install.log"
# ==============================================================================

echo "Початок процесу розгортання на сервер..."
sleep 2

# 1. Оновлення системи та встановлення базових утиліт
echo "--> Оновлення системних пакетів..."

sudo apt update && sudo apt full-upgrade -y 
&& 
sudo apt autoremove --purge -y 
&& 
sudo snap refresh 
&& 
echo "Checking for remaining upgrades..." 
&& 
apt list --upgradable 
&& 
echo "Checking snap health..." 
&& 
snap list

apt-get install -y curl wget software-properties-common ufw nginx

ufw allow 22
ufw allow 25
ufw allow 587
ufw allow 143
ufw allow 80
ufw allow 443
ufw allow 8090
ufw --force enable

# 2. Перевірка та встановлення Git
if ! command -v git &> /dev/null; then
    echo "--> Встановлення Git..."
    apt-get install -y git
else
    echo "--> Git вже встановлено."
fi

# Створення користувача для застосунку (якщо не існує)
if ! id -u "$APP_USER" >/dev/null 2>&1; then
    log "Створення користувача $APP_USER..."
    useradd -m -s /bin/bash "$APP_USER"
fi

# 6. Клонування репозиторію
if [ ! -d "$APP_DIR" ]; then
    log "Клонування репозиторію з $REPO_URL..."
    git clone --depth 1 "$REPO_URL" "$APP_DIR" >> "$LOG_FILE" 2>&1
    chown -R "$APP_USER":"$APP_USER" "$APP_DIR"
else
    log "Директорія застосунку $APP_DIR вже існує, оновлення коду (git pull)..."
    sudo -u "$APP_USER" -H bash -c "cd $APP_DIR && git fetch && git reset --hard origin/main" >> "$LOG_FILE" 2>&1
fi

# 7. Перевірка та встановлення Python 3.12
if ! command -v python3.12 &> /dev/null; then
    log "Встановлення Python 3.12..."
    add-apt-repository ppa:deadsnakes/ppa -y >> "$LOG_FILE" 2>&1
    apt-get update -y >> "$LOG_FILE" 2>&1
    apt-get install -y python3.12 python3.12-venv python3.12-dev build-essential >> "$LOG_FILE" 2>&1
else
    log "Python 3.12 вже встановлено."
fi

# 8. Розгортання віртуального оточення та створення .env файлу
log "Налаштування віртуального оточення..."
if [ ! -d "$APP_DIR/venv" ]; then
    sudo -u "$APP_USER" -H bash -c "cd $APP_DIR && python3.12 -m venv venv" >> "$LOG_FILE" 2>&1
fi
sudo -u "$APP_USER" -H bash -c "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt" >> "$LOG_FILE" 2>&1 || log "requirements.txt не знайдено, пропускаємо"

if [ ! -f "$APP_DIR/.env" ]; then
    log "Створення конфігураційного файлу .env..."
    cat <<EOF > "$APP_DIR/.env"
# SMTP Configuration (Postfix на тому ж хості)
SMTP_SERVER=localhost
SMTP_PORT=587
SMTP_USER=<ВСТАВТЕ_КОРИСТУВАЧА_SMTP>
SMTP_PASSWORD=<ВСТАВТЕ_ПАРОЛЬ_SMTP>

# IMAP Configuration (Dovecot на тому ж хості)
IMAP_SERVER=localhost
IMAP_PORT=143
IMAP_USER=<ВСТАВТЕ_КОРИСТУВАЧА_IMAP>
IMAP_PASSWORD=<ВСТАВТЕ_ПАРОЛЬ_IMAP>

# App Settings
APP_PORT=$APP_PORT
DEBUG=False

SUDO_USER_PASSWORD=<ВСТАВТЕ_ПАРОЛЬ_КОРИСТУВАЧА_СИСТЕМИ>
MAIL_VALIDATE_CERTS=False
DOMAIN=$DOMAIN_NAME
DISPLAY_TIMEZONE=Europe/Berlin
EOF
    chown "$APP_USER":"$APP_USER" "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
else
    log "Файл .env вже існує, пропускаємо створення."
fi

# 9. Генерація самопідписаних сертифікатів (якщо не існують)
if [ ! -f "$CERT_DIR/postfix.pem" ]; then
    log "Створення самопідписаних SSL сертифікатів для поштових сервісів..."
    mkdir -p "$CERT_DIR"
    openssl req -new -x509 -days 3650 -nodes -out "$CERT_DIR/postfix.pem" -keyout "$CERT_DIR/postfix.key" -subj "/C=UA/ST=Kyiv/L=Kyiv/O=IT/CN=$DOMAIN_NAME" >> "$LOG_FILE" 2>&1
    chmod 600 "$CERT_DIR/postfix.key"
    chmod 644 "$CERT_DIR/postfix.pem"
else
    log "SSL сертифікати вже існують."
fi

# 10. Налаштування Postfix через postconf (Безпечна модифікація, без затирання)
log "Налаштування Postfix..."
postconf -e "smtpd_banner = \$myhostname ESMTP"
postconf -e "biff = no"
postconf -e "append_dot_mydomain = no"
postconf -e "readme_directory = no"
postconf -e "compatibility_level = 3.6"
postconf -e "smtpd_tls_cert_file = $CERT_DIR/postfix.pem"
postconf -e "smtpd_tls_key_file = $CERT_DIR/postfix.key"
postconf -e "smtpd_tls_security_level = may"
postconf -e "smtp_tls_CApath = /etc/ssl/certs"
postconf -e "smtp_tls_security_level = may"
postconf -e "smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache"
postconf -e "smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination"
postconf -e "myhostname = $DOMAIN_NAME"
postconf -e "mydomain = $DOMAIN_NAME"
postconf -e "myorigin = \$mydomain"
postconf -e "alias_maps = hash:/etc/aliases"
postconf -e "alias_database = hash:/etc/aliases"
postconf -e "mydestination = \$myhostname, localhost, \$mydomain"
postconf -e "mynetworks = 127.0.0.0/8 172.0.0.0/8 10.0.0.0/8 100.64.0.0/10"
postconf -e "mailbox_size_limit = 0"
postconf -e "recipient_delimiter = +"
postconf -e "inet_interfaces = all"
postconf -e "inet_protocols = ipv4"
postconf -e "home_mailbox = Maildir/"
postconf -e "smtp_tls_wrappermode = no"
postconf -e "mailbox_command = /usr/bin/procmail -a \"\$EXTENSION\""
postconf -e "smtpd_tls_loglevel = 1"
postconf -e "smtp_tls_loglevel = 1"

# 11. Налаштування Dovecot (Без затирання основного файлу, створюємо drop-in config)
log "Налаштування Dovecot..."
cat <<EOF > /etc/dovecot/local.conf
auth_mechanisms = plain login
disable_plaintext_auth = no
mail_location = maildir:~/Maildir
mail_privileged_group = mail

namespace inbox {
  inbox = yes
  location = 
  mailbox Drafts {
    special_use = \Drafts
  }
  mailbox Junk {
    special_use = \Junk
  }
  mailbox Sent {
    special_use = \Sent
  }
  mailbox "Sent Messages" {
    special_use = \Sent
  }
  mailbox Trash {
    special_use = \Trash
  }
  prefix = 
}

passdb {
  driver = pam
}

protocols = " imap pop3"

service auth {
  unix_listener /var/spool/postfix/private/auth {
    group = postfix
    mode = 0660
    user = postfix
  }
  unix_listener auth-userdb {
    mode = 0600
    user = dovecot
  }
}

service imap-login {
  inet_listener imap {
    port = 143
  }
}

ssl_cert = <$CERT_DIR/postfix.pem
ssl_key = <$CERT_DIR/postfix.key
ssl_client_ca_dir = /etc/ssl/certs

userdb {
  driver = passwd
}
EOF

# 12. Налаштування Nginx як Reverse Proxy
log "Налаштування Nginx..."
cat <<EOF > /etc/nginx/sites-available/mailservice
server {
    listen 80;
    server_name $DOMAIN_NAME;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /monitoring/ {
        proxy_pass http://127.0.0.1:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /nginx_status {
        stub_status;
        allow 127.0.0.1;
        allow 172.16.0.0/12;
        deny all;
    }
}
EOF

ln -sf /etc/nginx/sites-available/mailservice /etc/nginx/sites-enabled/mailservice
rm -f /etc/nginx/sites-enabled/default

# 13. Налаштування Systemd для API Застосунку
log "Створення systemd сервісу для API..."
cat <<EOF > /etc/systemd/system/mail-api.service
[Unit]
Description=Mail Service API
After=network.target postfix.service dovecot.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$APP_PORT --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 14. Перезапуск сервісів та активація
log "Перезапуск та активація сервісів..."
systemctl daemon-reload
systemctl enable postfix dovecot spamassassin mail-api nginx >> "$LOG_FILE" 2>&1
systemctl restart postfix dovecot spamassassin mail-api nginx >> "$LOG_FILE" 2>&1

# 15. Фінальне повідомлення
IP_ADDRESS=$(hostname -I | awk '{print $1}')
log "Встановлення успішно завершено!"

echo "=========================================================================="
echo "✅ Встановлення та налаштування сервера успішно завершено!"
echo "=========================================================================="
echo "Застосунок API доступний за адресою: http://$IP_ADDRESS або http://$DOMAIN_NAME"
echo " (Також доступний напряму для тестів: http://$IP_ADDRESS:$APP_PORT)"
echo ""
echo "Служби які зараз працюють:"
echo "- Nginx (Reverse Proxy на порту 80)"
echo "- Postfix (SMTP)"
echo "- Dovecot (IMAP/POP3)"
echo "- Mail Service API (Gunicorn/Uvicorn)"
echo "- SpamAssassin"
echo ""
echo "⚠️ УВАГА ⚠️"
echo "Перед повноцінною роботою заповніть паролі у файлі: $APP_DIR/.env"
echo "Для рестарту API після зміни налаштувань використовуйте:"
echo "sudo systemctl restart mail-api"
echo "Детальний лог виконання знаходиться в: $LOG_FILE"
echo "=========================================================================="
