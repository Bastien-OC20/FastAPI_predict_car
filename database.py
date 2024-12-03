from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Informations de connexion
DB_HOST = "mysql-babaste.alwaysdata.net"
DB_USER = "babaste"
DB_PASSWORD = "Simplon"
DB_NAME = "babaste_predict_car"
DB_PORT = 3306

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Tester la connexion
# def test_connection():
#     try:
#         # Créer une session
#         session = SessionLocal()
#         # Exécuter une simple requête
#         session.execute(text("SELECT 1"))
#         print("Connexion réussie")
#     except Exception as e:
#         print(f"Erreur de connexion : {e}")
#     finally:
#         session.close()

# if __name__ == "__main__":
#     test_connection()