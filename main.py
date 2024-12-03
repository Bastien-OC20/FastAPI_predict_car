import os
from fastapi import FastAPI, HTTPException, Depends, status
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, get_db
import joblib
import pandas as pd
import logging
from utils import get_password_hash, verify_password

SECRET_KEY = os.getenv("SECRET_KEY", " your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configurer le logging
logging.basicConfig(level=logging.INFO)

# Configurer le contexte de hachage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

app = FastAPI()

# Configurer CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://fastapi-predict-car.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

class PredictRequest(BaseModel):
    kilometrage: float
    annee: int
    marque: str
    carburant: str
    transmission: str
    modele: str
    etat: str

    class Config:
        schema_extra = {
            "example": {
                "kilometrage": 15000,
                "annee": 2019,
                "marque": "Peugeot",
                "carburant": "Essence",
                "transmission": "Manuelle",
                "modele": "208",
                "etat": "Occasion",
            }
        }

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
                "carburant": "Carburant",
                "transmission": "Transmission",
                "modele": "Modele",
                "etat": "Etat",
            }
        )
        logging.info(f"Input data with correct column names: {input_data}")

        # Faire la prédiction directement avec le modèle Gradient Boosting
        rf_prediction = Gradient_Boosting_model.predict(input_data)[0]
        logging.info(f"Gradient Boosting prediction: {rf_prediction}")

        # Faire la prédiction directement avec le modèle de régression logistique
        lr_prediction = Logistic_Regression_model.predict(input_data)[0]
        logging.info(f"Logistic Regression prediction: {lr_prediction}")

        # Déterminer si le prix est bon ou mauvais
        price_evaluation = "Abordable" if lr_prediction == 1 else "Pas abordable"

        return {
            "Gradient_Boosting_prediction": float(rf_prediction),
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
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        nom=user.nom, email=user.email, hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        nom: str = payload.get("sub")
        if nom is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=nom)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data.username)
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

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
