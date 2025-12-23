"""
Module de gestion de la base de données pour ModelSelector
"""
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import json

Base = declarative_base()


class ModelCatalogue(Base):
    """Catalogue des modèles avec leurs métadonnées"""
    __tablename__ = "model_catalogue"

    id = Column(String, primary_key=True, index=True)
    model_name = Column(String, unique=True, index=True)
    category = Column(String)
    task_types = Column(JSON)
    supports_sparse = Column(String)
    requires_gpu = Column(String)
    min_samples = Column(Integer)
    max_features = Column(Integer, nullable=True)
    recommended_for_text = Column(String)
    recommended_for_images = Column(String)
    recommended_for_tabular = Column(String)
    default_hyperparameters = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelSelection(Base):
    """Historique des sélections de modèles"""
    __tablename__ = "model_selections"

    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    dataset_path = Column(String)
    task_type = Column(String)
    metric = Column(String)
    selected_models = Column(JSON)  # Liste des modèles sélectionnés avec scores
    selection_config = Column(JSON)  # Configuration utilisée pour la sélection
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelCompatibility(Base):
    """Cache des compatibilités modèle/dataset"""
    __tablename__ = "model_compatibilities"

    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, index=True)
    model_name = Column(String, index=True)
    compatibility_score = Column(Float)
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mluser:mlpass@localhost:5432/microlearn"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialiser les tables de la base de données"""
    Base.metadata.create_all(bind=engine)


def save_model_selection(dataset_id: str, dataset_path: str, task_type: str, 
                         metric: str, selected_models: list, config: dict) -> ModelSelection:
    """Sauvegarder une sélection de modèles"""
    db = SessionLocal()
    try:
        selection = ModelSelection(
            id=f"selection_{datetime.utcnow().timestamp()}",
            dataset_id=dataset_id,
            dataset_path=dataset_path,
            task_type=task_type,
            metric=metric,
            selected_models=selected_models,
            selection_config=config
        )
        db.add(selection)
        db.commit()
        db.refresh(selection)
        return selection
    finally:
        db.close()


def get_model_selection(dataset_id: str) -> list:
    """Récupérer les sélections de modèles pour un dataset"""
    db = SessionLocal()
    try:
        selections = db.query(ModelSelection).filter(
            ModelSelection.dataset_id == dataset_id
        ).order_by(ModelSelection.created_at.desc()).all()
        
        return [
            {
                "id": s.id,
                "dataset_id": s.dataset_id,
                "task_type": s.task_type,
                "metric": s.metric,
                "selected_models": s.selected_models,
                "created_at": s.created_at.isoformat()
            }
            for s in selections
        ]
    finally:
        db.close()


def save_model_compatibility(dataset_id: str, model_name: str, 
                            score: float, reason: str) -> ModelCompatibility:
    """Sauvegarder une compatibilité modèle/dataset"""
    db = SessionLocal()
    try:
        compatibility = ModelCompatibility(
            id=f"comp_{dataset_id}_{model_name}_{datetime.utcnow().timestamp()}",
            dataset_id=dataset_id,
            model_name=model_name,
            compatibility_score=score,
            reason=reason
        )
        db.add(compatibility)
        db.commit()
        db.refresh(compatibility)
        return compatibility
    finally:
        db.close()


def get_model_compatibility(dataset_id: str, model_name: str) -> dict:
    """Récupérer la compatibilité d'un modèle avec un dataset"""
    db = SessionLocal()
    try:
        comp = db.query(ModelCompatibility).filter(
            ModelCompatibility.dataset_id == dataset_id,
            ModelCompatibility.model_name == model_name
        ).order_by(ModelCompatibility.created_at.desc()).first()
        
        if comp:
            return {
                "model_name": comp.model_name,
                "compatibility_score": comp.compatibility_score,
                "reason": comp.reason,
                "created_at": comp.created_at.isoformat()
            }
        return None
    finally:
        db.close()


def save_model_to_catalogue(model_data: dict) -> ModelCatalogue:
    """Ajouter un modèle au catalogue"""
    db = SessionLocal()
    try:
        model = ModelCatalogue(
            id=model_data.get("name", f"model_{datetime.utcnow().timestamp()}"),
            model_name=model_data["name"],
            category=model_data.get("category"),
            task_types=model_data.get("task_types", []),
            supports_sparse=str(model_data.get("supports_sparse", False)),
            requires_gpu=str(model_data.get("requires_gpu", False)),
            min_samples=model_data.get("min_samples", 10),
            max_features=model_data.get("max_features"),
            recommended_for_text=str(model_data.get("recommended_for_text", False)),
            recommended_for_images=str(model_data.get("recommended_for_images", False)),
            recommended_for_tabular=str(model_data.get("recommended_for_tabular", True)),
            default_hyperparameters=model_data.get("hyperparameters", {})
        )
        db.merge(model)  # Utiliser merge pour éviter les doublons
        db.commit()
        db.refresh(model)
        return model
    finally:
        db.close()


def get_model_from_catalogue(model_name: str) -> dict:
    """Récupérer un modèle du catalogue"""
    db = SessionLocal()
    try:
        model = db.query(ModelCatalogue).filter(
            ModelCatalogue.model_name == model_name
        ).first()
        
        if model:
            return {
                "name": model.model_name,
                "category": model.category,
                "task_types": model.task_types,
                "supports_sparse": model.supports_sparse.lower() == "true",
                "requires_gpu": model.requires_gpu.lower() == "true",
                "min_samples": model.min_samples,
                "max_features": model.max_features,
                "recommended_for_text": model.recommended_for_text.lower() == "true",
                "recommended_for_images": model.recommended_for_images.lower() == "true",
                "recommended_for_tabular": model.recommended_for_tabular.lower() == "true",
                "hyperparameters": model.default_hyperparameters
            }
        return None
    finally:
        db.close()


# Initialiser la base de données au démarrage
init_db()

