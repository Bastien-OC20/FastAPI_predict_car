from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Carburant(BaseModel):
    id_carburant: int
    type: str

    class Config:
        from_attribute = True

class Transmission(BaseModel):
    id_transmission: int
    type: str

    class Config:
        from_attribute = True

class Marque(BaseModel):
    id_marque: int
    nom: str

    class Config:
        from_attribute = True

class Modele(BaseModel):
    id_modele: int
    nom: str
    marque_id: int

    class Config:
        from_attribute = True

class VehiculeBase(BaseModel):
    annee: Optional[int] = None
    kilometrage: Optional[float] = None
    prix: Optional[float] = None
    etat: Optional[str] = None
    marque_id: Optional[int] = None
    modele_id: Optional[int] = None
    carburant_id: Optional[int] = None
    transmission_id: Optional[int] = None

class VehiculeCreate(VehiculeBase):
    pass

class PredictRequest(BaseModel):
    kilometrage: float
    annee: int
    marque: str
    carburant: str
    transmission: str
    modele: str
    etat: str

    class Config:
        json_schema_extra = {
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

class VehiculeUpdate(VehiculeBase):
    pass

class Vehicule(VehiculeBase):
    id: int
    carburant: Optional[Carburant] = None
    transmission: Optional[Transmission] = None
    modele: Optional[Modele] = None
    marque: Optional[Marque] = None

    class Config:
        from_attribute = True

class UserBase(BaseModel):
    nom: str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    profile_image: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attribute = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
