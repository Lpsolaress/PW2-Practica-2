import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.security import verify_password, get_password_hash

def test_security():
    password = "admin123password"
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    
    result = verify_password(password, hashed)
    print(f"Verificación: {'EXITOSA' if result else 'FALLIDA'}")
    
    # Probar con un hash real de la DB (copiado del log anterior)
    db_hash = "$2b$12$VlTXsRQH65Hv3W4qlz.LC.WoLQ598hNdqtOF1WDUgotAEPC61LZLm"
    result_db = verify_password(password, db_hash)
    print(f"Verificación con hash de DB: {'EXITOSA' if result_db else 'FALLIDA'}")

if __name__ == "__main__":
    test_security()
