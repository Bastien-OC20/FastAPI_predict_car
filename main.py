import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import joblib
from catboost import CatBoostClassifier
import pandas as pd
import logging
from utils import get_password_hash, verify_password  # Importer les fonctions de hachage

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Import des modules locaux
import models, schemas, crud
from database import SessionLocal, engine

# Configuration des variables globales
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurer le logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialiser l'application FastAPI
app = FastAPI()

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter le dossier static pour servir le fichier favicon.ico
app.mount("/static/", StaticFiles(directory="static"), name="static")

# Dépendance pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Charger les modèles nécessaires
try:
    catboost_model = joblib.load("./models/pkl/catboost_model.pkl")
except FileNotFoundError:
    print("Le fichier catboost_model.pkl est introuvable.")
except Exception as e:
    print(f"Erreur lors du chargement du modèle CatBoost : {e}")

Logistic_Regression_model = joblib.load("./models/pkl/Logistic_Regression_model.pkl")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prédiction de prix de voitures"}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_nom(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = crud.authenticate_user_by_nom(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.nom}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/vehicules/", response_model=list[schemas.Vehicule])
def read_vehicules(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_vehicules(db, skip=skip, limit=limit)


@app.get("/vehicules/{vehicule_id}", response_model=schemas.Vehicule)
def read_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    vehicule = crud.get_vehicule(db, vehicule_id=vehicule_id)
    if vehicule is None:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return vehicule

@app.post("/vehicules/", response_model=schemas.Vehicule, status_code=201)
def create_vehicule(vehicule: schemas.VehiculeCreate, db: Session = Depends(get_db)):
    return crud.create_vehicule(db=db, vehicule=vehicule)

@app.put("/vehicules/{vehicule_id}", response_model=schemas.Vehicule)
def update_vehicule(vehicule_id: int, vehicule_update: schemas.VehiculeUpdate, db: Session = Depends(get_db)):
    db_vehicule = crud.update_vehicule(db=db, vehicule_id=vehicule_id, vehicule_update=vehicule_update)
    if db_vehicule is None:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return db_vehicule

@app.delete("/vehicules/{vehicule_id}", response_model=dict)
def delete_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    return crud.delete_vehicule(db=db, vehicule_id=vehicule_id)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    return crud.update_user(db=db, user_id=user_id, user_update=user)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return crud.delete_user(db=db, user_id=user_id)


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post("/predict")
def predict(request: schemas.PredictRequest):

    try:
        # Convertir les données de la requête en DataFrame
        input_data = pd.DataFrame([request.model_dump()])
        logging.info(f"Input data: {input_data}")

        # Renommer les colonnes pour correspondre à celles utilisées lors de l'entraînement
        input_data = input_data.rename(
            columns={
                "kilometrage": "Kilometrage",
                "annee": "Annee",
                "marque": "Marque",
                "finition": "Finition",
                "carburant": "Carburant",
                "transmission": "Transmission",
                "modele": "Modele",
                "etat": "Etat",
            }
        )
        logging.info(f"Input data with correct column names: {input_data}")

        # Faire la prédiction directement avec le modèle CatBoosting
        cb_prediction = catboost_model.predict(input_data)[0]
        logging.info(f"CatBoost prediction: {cb_prediction}")

        # Faire la prédiction directement avec le modèle de régression logistique
        lr_prediction = Logistic_Regression_model.predict(input_data)[0]
        logging.info(f"Logistic Regression prediction: {lr_prediction}")

        # Déterminer si le prix est bon ou mauvais
        price_evaluation = "Abordable" if lr_prediction == 1 else "Pas abordable"

        return {
            "catboost_prediction": float(cb_prediction),
            "Logistic_Regression_evaluation": price_evaluation,
        }

    except Exception as e:
        logging.error(f"Erreur lors de la prédiction: {e}")
        raise HTTPException(status_code=400, detail="Erreur lors de la prédiction")


@app.post("/login", response_model=schemas.User)
def login(nom: str, password: str, db: Session = Depends(get_db)):
    user = crud.authenticate_user_by_nom(db, nom, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return user


@app.post("/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe déjà
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    # Créer un nouvel utilisateur
    password = get_password_hash(user.password)
    new_user = models.User(
        nom=user.nom, email=user.email, password=password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/update-password")
def update_password(email: str, new_password: str, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur existe
    db_user = crud.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Mettre à jour le mot de passe
    password = get_password_hash(new_password)
    db_user.password = password
    db.commit()
    db.refresh(db_user)

    return {"message": "Mot de passe mis à jour avec succès"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
