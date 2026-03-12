import os

# Базова адреса API
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8090").rstrip("/")

# Префікс для тестових користувачів, щоб їх було легше знайти та видалити
TEST_USER_PREFIX = os.getenv("TEST_USER_PREFIX", "test_e2e_")

# Дефолтний пароль для тестів
DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "SecurePass123!")

# Домен за замовчуванням
DOMAIN = os.getenv("DOMAIN", "localhost")
