import os
import sys

# Додаємо кореневу директорію проекту до sys.path для імпортів
sys.path.append(os.getcwd())

from tests.e2e.api import test_users, test_mail
from tests.e2e.ui import test_auth_ui, test_mail_ui, test_system_ui
from tests import load_test

def run_all():
    print("========================================")
    print("START DES VOLLSTÄNDIGEN E2E-TESTZYKLUS")
    print("========================================\n")
    
    test_modules = [
        test_users,
        test_mail,
        test_auth_ui,
        test_mail_ui,
        test_system_ui
    ]
    
    passed = 0
    failed = 0
    
    for module in test_modules:
        try:
            # Виконуємо основну логіку модуля
            # Можна було б додати автоматичний пошук функцій test_*, 
            # але для простоти викликаємо внутрішні методи або перевіряємо __name__
            if hasattr(module, 'test_user_lifecycle'):
                module.test_user_lifecycle()
                module.test_delete_user_invalid_password()
                module.test_create_user_invalid()
                module.test_access_alien_data()
            elif hasattr(module, 'test_mail_flow'):
                module.test_mail_flow()
                module.test_send_mail_invalid()
                module.test_api_access_alien_mail()
            elif hasattr(module, 'test_ui_registration_and_login'):
                module.test_ui_registration_and_login()
                module.test_ui_change_password()
                module.test_ui_delete_user()
                module.test_ui_login_invalid()
                module.test_ui_unauthorized_access()
                module.test_ui_registration_validation()
                module.test_ui_change_password_invalid()
                module.test_ui_delete_user_invalid_confirm()
            elif hasattr(module, 'test_ui_mail_cycle'):
                module.test_ui_mail_cycle()
                module.test_ui_compose_empty_fields()
                module.test_ui_cross_user_mail()
            elif hasattr(module, 'test_ui_system_pages'):
                module.test_ui_system_pages()
                
            print(f"MODUL {module.__name__} BESTANDEN.\n")
            passed += 1
        except Exception as e:
            print(f"!!! FEHLER IM MODUL {module.__name__}: {e}\n")
            failed += 1

    print("========================================")
    print(f"ERGEBNISSE: Bestanden {passed}, Fehlgeschlagen {failed}")
    print("========================================")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    # Start der regulären E2E-Tests
    run_all()
    
    # Start der Lasttests nach erfolgreichem Abschluss der Haupttests
    load_test.run_load_test(num_users=10, rounds=3)
