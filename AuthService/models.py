from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base
import datetime

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    # Mapping: attribut python 'username' <-> colonne DB 'nom'
    username = Column("nom", String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # Mapping: attribut python 'hashed_password' <-> colonne DB 'mot_de_passe'
    hashed_password = Column("mot_de_passe", String)
    
    # Colonne existante en DB
    date_creation = Column(DateTime, default=datetime.datetime.utcnow)

    # Propriétés calculées / par défaut pour la compatibilité avec le reste du code
    @property
    def full_name(self):
        return self.username # Utilise le nom comme full_name par défaut
        
    @property
    def disabled(self):
        return False # Par défaut, utilisateur actif car pas de colonne 'disabled'
