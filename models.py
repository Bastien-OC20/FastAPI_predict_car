from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from database import Base
from sqlalchemy.orm import relationship

class Vehicule(Base):
    __tablename__ = "Vehicule"
    id = Column("ID_Vehicule", Integer, primary_key=True, index=True)
    annee = Column("Annee", Integer)
    kilometrage = Column("Kilometrage", Float)
    prix = Column("Prix", Float)
    etat = Column("Etat", String)
    marque_id = Column("Marque_ID", Integer, ForeignKey("Marque.ID_Marque"))
    modele_id = Column("Modele_ID", Integer, ForeignKey("Modele.ID_Modele"), index=True)
    finition_id = Column("Finition_ID", Integer, ForeignKey("Finition.ID_Finition"), index=True)
    carburant_id = Column("Carburant_ID", Integer, ForeignKey("Carburant.ID_Carburant"), index=True)
    transmission_id = Column("Transmission_ID", Integer, ForeignKey("Transmission.ID_Transmission"), index=True)

    # Relations
    carburant = relationship("Carburant", back_populates="vehicules", lazy="joined")
    transmission = relationship("Transmission", back_populates="vehicules", lazy="joined")
    modele = relationship("Modele", back_populates="vehicules", lazy="joined")
    marque = relationship("Marque", back_populates="vehicules", lazy="joined")
    finition = relationship("Finition", back_populates="vehicules", lazy="joined")

class Carburant(Base):
    __tablename__ = "Carburant"
    id = Column("ID_Carburant", Integer, primary_key=True, index=True)
    type = Column("Type", String, nullable=False)
    
    # Relation inverse
    vehicules = relationship("Vehicule", back_populates="carburant")

class Transmission(Base):
    __tablename__ = "Transmission"
    id = Column("ID_Transmission", Integer, primary_key=True, index=True)
    type = Column("Type", String, nullable=False)
    
    # Relation inverse
    vehicules = relationship("Vehicule", back_populates="transmission")

class Marque(Base):
    __tablename__ = "Marque"
    id = Column("ID_Marque", Integer, primary_key=True, index=True)
    name = Column("Nom", String, index=True)
    
    # Relation inverse
    vehicules = relationship("Vehicule", back_populates="marque")

class Modele(Base):
    __tablename__ = "Modele"
    id = Column("ID_Modele", Integer, primary_key=True, index=True)
    name = Column("Nom", String, index=True)
    marque_id = Column("Marque_ID", Integer, ForeignKey("Marque.ID_Marque"))
    
    # Relation inverse
    vehicules = relationship("Vehicule", back_populates="modele")

class Finition(Base):
    __tablename__ = "Finition"
    id = Column("ID_Finition", Integer, primary_key=True, index=True)
    name = Column("Nom", String, index=True)
    marque_id = Column("Marque_ID", Integer, ForeignKey("Marque.ID_Marque"))
    
    # Relation inverse
    vehicules = relationship("Vehicule", back_populates="finition")

class User(Base):
    __tablename__ = "Users"
    id = Column("ID_User", Integer, primary_key=True, index=True)
    email = Column("Email", String, unique=True, index=True, nullable=False)
    nom = Column("Nom", String, nullable=False)
    password = Column("Password", String, nullable=False)
    is_active = Column("Is_Active", Boolean, default=True)
    is_superuser = Column("Is_Superuser", Boolean, default=False)
    profile_image = Column("Profile_Image", String, nullable=True)
