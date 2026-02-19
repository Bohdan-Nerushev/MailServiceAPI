#!/bin/bash

# Скрипт для налаштування поштового сервера (Postfix + Dovecot)
# для роботи з Mail Service API

# Перевірка на права root
if [[ $EUID -ne 0 ]]; then
   echo "Будь ласка, запустіть скрипт через sudo"
   exit 1
fi

DOMAIN="lws.local"
echo "--- Починаємо встановлення для домену $DOMAIN ---"

# 1. Оновлення репозиторіїв
apt update

# 2. Встановлення Postfix та Dovecot
echo "встановлення Postfix та Dovecot..."
# DEBIAN_FRONTEND=noninteractive дозволяє уникнути діалогових вікон
export DEBIAN_FRONTEND=noninteractive
apt install -y postfix dovecot-imapd dovecot-pop3d

# 3. Налаштування Postfix
echo "Налаштування Postfix..."
postconf -e "myhostname = mail.$DOMAIN"
postconf -e "mydestination = \$myhostname, $DOMAIN, localhost.localdomain, localhost"
postconf -e "home_mailbox = Maildir/"
postconf -e "mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128"

# 4. Налаштування Dovecot (Maildir та Auth)
echo "Налаштування Dovecot..."
# Вказуємо Dovecot шукати пошту в папці Maildir користувача
sed -i 's/^#mail_location = .*/mail_location = maildir:~\/Maildir/' /etc/dovecot/conf.d/10-mail.conf

# Дозволяємо аутентифікацію без SSL (для локальних тестів)
sed -i 's/^#disable_plaintext_auth = .*/disable_plaintext_auth = no/' /etc/dovecot/conf.d/10-auth.conf
sed -i 's/^ssl = .*/ssl = yes/' /etc/dovecot/conf.d/10-ssl.conf

# 5. Створення структури Maildir для нових користувачів
echo "Налаштування шаблону /etc/skel..."
mkdir -p /etc/skel/Maildir/{cur,new,tmp}
chmod -R 700 /etc/skel/Maildir

# 6. Перезапуск сервісів
echo "Перезапуск сервісів..."
systemctl restart postfix
systemctl restart dovecot
systemctl enable postfix
systemctl enable dovecot

echo "--- Встановлення завершено! ---"
echo "Тепер ви можете використовувати API для створення користувачів та відправки пошти."
