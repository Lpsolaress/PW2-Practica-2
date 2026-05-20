import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Añadir el directorio actual al path para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.usuario import Usuario
from app.database import DATABASE_URL

def check_db():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        admin = db.query(Usuario).filter(Usuario.email == "admin@nuba.com").first()
        if admin:
            print(f"Usuario encontrado: {admin.username}")
            print(f"Email: {admin.email}")
            print(f"Rol: {admin.role}")
            print(f"Hash en DB: {admin.hashed_password}")
        else:
            print("Usuario admin@nuba.com NO encontrado en la base de datos.")
            
        users = db.query(Usuario).all()
        print(f"\nTotal de usuarios en DB: {len(users)}")
        for u in users:
            print(f"- {u.email} ({u.role})")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db()
