import os

# Basis-URL der API
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8090").rstrip("/")
#BASE_URL = os.getenv("BASE_URL", "http://172.18.6.162:80").rstrip("/")
# Präfix für Testbenutzer, um sie leichter finden und löschen zu können
TEST_USER_PREFIX = os.getenv("TEST_USER_PREFIX", "test_e2e_")

# Standardpasswort für Tests
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "SecurePass123!")

# Standard-Domain
DOMAIN = os.getenv("DOMAIN", "localhost")
