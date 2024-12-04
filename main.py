import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import joblib
import pandas as pd
import logging

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Import des modules locaux
import models, schemas, crud
from database import SessionLocal, engine
from utils import get_password_hash, verify_password

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
    allow_origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://fastapi-predict-car.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendance pour obtenir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Charger les modèles nécessaires
Gradient_Boosting_model = joblib.load("./models/pkl/Gradient_Boosting_model.pkl")
Logistic_Regression_model = joblib.load("./models/pkl/Logistic_Regression_model.pkl")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# Routes
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.head("/")
def read_root_head():
    return {"message": "Bienvenue sur l'API de prédiction de prix de voitures"}

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
def update_vehicule(
    vehicule_id: int,
    vehicule_update: schemas.VehiculeUpdate,
    db: Session = Depends(get_db),
):
    db_vehicule = crud.update_vehicule(
        db=db, vehicule_id=vehicule_id, vehicule_update=vehicule_update
    )
    if db_vehicule is None:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    return db_vehicule

@app.delete("/vehicules/{vehicule_id}", response_model=dict)
def delete_vehicule(vehicule_id: int, db: Session = Depends(get_db)):
    return crud.delete_vehicule(db=db, vehicule_id=vehicule_id)

@app.post("/predict")
def predict(request: schemas.PredictRequest):
    try:
        # Convertir les données en DataFrame
        input_data = pd.DataFrame([request.dict()])
        logging.info(f"Données d'entrée : {input_data}")

        # Renommer les colonnes
        input_data = input_data.rename(columns=str.capitalize)
        logging.info(f"Données renommees : {input_data}")

        # Faire les prédictions
        rf_prediction = Gradient_Boosting_model.predict(input_data)[0]
        lr_prediction = Logistic_Regression_model.predict(input_data)[0]

        price_evaluation = "Abordable" if lr_prediction == 1 else "Pas abordable"

        return {
            "Gradient_Boosting_prediction": float(rf_prediction),
            "Logistic_Regression_evaluation": price_evaluation,
        }
    except Exception as e:
        logging.error(f"Erreur lors de la prédiction : {e}")
        raise HTTPException(status_code=400, detail="Erreur lors de la prédiction")

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

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
