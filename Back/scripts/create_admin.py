import os
import sys

# Añadir el directorio actual al path para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models.usuario import Usuario
from app.services.security import get_password_hash

def create_admin():
    # Asegurar que las tablas existen
    init_db()
    
    db = SessionLocal()
    try:
        # Datos del administrador
        admin_email = "admin@nuba.com"
        admin_username = "admin"
        admin_password = "admin123password"
        
        # Verificar si ya existe
        existing_admin = db.query(Usuario).filter(Usuario.email == admin_email).first()
        if existing_admin:
            print(f"El administrador con email {admin_email} ya existe.")
            existing_admin.role = "administrador"
            existing_admin.hashed_password = get_password_hash(admin_password)
            db.commit()
            print("Credenciales actualizadas.")
            return

        # Crear nuevo administrador
        new_admin = Usuario(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role="administrador"
        )
        
        db.add(new_admin)
        db.commit()
        print(f"Administrador creado exitosamente:")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        
    except Exception as e:
        print(f"Error al crear el administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
