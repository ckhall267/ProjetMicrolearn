"""
Module de sélection automatique de modèles basé sur les caractéristiques du dataset
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from enum import Enum


class TaskType(str, Enum):
    """Types de tâches ML supportées"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"


class ModelCategory(str, Enum):
    """Catégories de modèles"""
    CLASSICAL = "classical"
    ENSEMBLE = "ensemble"
    DEEP_LEARNING = "deep_learning"
    NEURAL_NETWORK = "neural_network"


class ModelCandidate:
    """Représente un modèle candidat"""
    def __init__(
        self,
        name: str,
        category: ModelCategory,
        task_types: List[TaskType],
        supports_sparse: bool = False,
        requires_gpu: bool = False,
        min_samples: int = 10,
        max_features: Optional[int] = None,
        recommended_for_text: bool = False,
        recommended_for_images: bool = False,
        recommended_for_tabular: bool = True,
        hyperparameters: Optional[Dict] = None
    ):
        self.name = name
        self.category = category
        self.task_types = task_types
        self.supports_sparse = supports_sparse
        self.requires_gpu = requires_gpu
        self.min_samples = min_samples
        self.max_features = max_features
        self.recommended_for_text = recommended_for_text
        self.recommended_for_images = recommended_for_images
        self.recommended_for_tabular = recommended_for_tabular
        self.hyperparameters = hyperparameters or {}
        self.compatibility_score = 0.0
        self.reason = ""

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category.value,
            "task_types": [t.value for t in self.task_types],
            "supports_sparse": self.supports_sparse,
            "requires_gpu": self.requires_gpu,
            "min_samples": self.min_samples,
            "max_features": self.max_features,
            "recommended_for_text": self.recommended_for_text,
            "recommended_for_images": self.recommended_for_images,
            "recommended_for_tabular": self.recommended_for_tabular,
            "hyperparameters": self.hyperparameters,
            "compatibility_score": self.compatibility_score,
            "reason": self.reason
        }


class ModelRegistry:
    """Registre des modèles disponibles avec leurs métadonnées"""
    
    @staticmethod
    def get_all_models() -> List[ModelCandidate]:
        """Retourne tous les modèles disponibles"""
        models = []
        
        # Classification models
        models.append(ModelCandidate(
            name="XGBoost",
            category=ModelCategory.ENSEMBLE,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            supports_sparse=True,
            recommended_for_tabular=True,
            hyperparameters={
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1
            }
        ))
        
        models.append(ModelCandidate(
            name="RandomForest",
            category=ModelCategory.ENSEMBLE,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            supports_sparse=True,
            recommended_for_tabular=True,
            hyperparameters={
                "n_estimators": 100,
                "max_depth": None,
                "min_samples_split": 2
            }
        ))
        
        models.append(ModelCandidate(
            name="SVM",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            supports_sparse=True,
            min_samples=50,
            max_features=10000,
            hyperparameters={
                "C": 1.0,
                "kernel": "rbf",
                "gamma": "scale"
            }
        ))
        
        models.append(ModelCandidate(
            name="LogisticRegression",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.CLASSIFICATION],
            supports_sparse=True,
            recommended_for_tabular=True,
            hyperparameters={
                "C": 1.0,
                "max_iter": 1000,
                "solver": "lbfgs"
            }
        ))
        
        models.append(ModelCandidate(
            name="DecisionTree",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "max_depth": None,
                "min_samples_split": 2
            }
        ))
        
        models.append(ModelCandidate(
            name="KNeighbors",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "n_neighbors": 5,
                "weights": "uniform"
            }
        ))
        
        models.append(ModelCandidate(
            name="NaiveBayes",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.CLASSIFICATION],
            supports_sparse=True,
            recommended_for_text=True,
            hyperparameters={
                "alpha": 1.0
            }
        ))
        
        models.append(ModelCandidate(
            name="CNN",
            category=ModelCategory.DEEP_LEARNING,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            requires_gpu=True,
            recommended_for_images=True,
            recommended_for_tabular=False,
            min_samples=1000,
            hyperparameters={
                "epochs": 50,
                "batch_size": 32,
                "learning_rate": 0.001
            }
        ))
        
        models.append(ModelCandidate(
            name="LSTM",
            category=ModelCategory.DEEP_LEARNING,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION, TaskType.TIME_SERIES],
            requires_gpu=True,
            recommended_for_text=True,
            recommended_for_tabular=False,
            min_samples=1000,
            hyperparameters={
                "epochs": 50,
                "batch_size": 32,
                "lstm_units": 64
            }
        ))
        
        models.append(ModelCandidate(
            name="GradientBoosting",
            category=ModelCategory.ENSEMBLE,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 3
            }
        ))
        
        models.append(ModelCandidate(
            name="AdaBoost",
            category=ModelCategory.ENSEMBLE,
            task_types=[TaskType.CLASSIFICATION, TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "n_estimators": 50,
                "learning_rate": 1.0
            }
        ))
        
        models.append(ModelCandidate(
            name="LinearRegression",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "fit_intercept": True
            }
        ))
        
        models.append(ModelCandidate(
            name="Ridge",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.REGRESSION, TaskType.CLASSIFICATION],
            recommended_for_tabular=True,
            hyperparameters={
                "alpha": 1.0
            }
        ))
        
        models.append(ModelCandidate(
            name="Lasso",
            category=ModelCategory.CLASSICAL,
            task_types=[TaskType.REGRESSION],
            recommended_for_tabular=True,
            hyperparameters={
                "alpha": 1.0
            }
        ))
        
        return models


class DatasetAnalyzer:
    """Analyse un dataset pour déterminer ses caractéristiques"""
    
    @staticmethod
    def analyze(dataset_path: str, target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse un dataset et retourne ses caractéristiques
        
        Args:
            dataset_path: Chemin vers le dataset (CSV)
            target_column: Nom de la colonne cible (optionnel)
        
        Returns:
            Dictionnaire avec les caractéristiques du dataset
        """
        try:
            df = pd.read_csv(dataset_path)
        except Exception as e:
            raise ValueError(f"Impossible de charger le dataset: {e}")
        
        # Déterminer le type de tâche
        task_type = TaskType.CLASSIFICATION
        if target_column and target_column in df.columns:
            target = df[target_column]
            if target.dtype in ['float64', 'int64']:
                unique_values = target.nunique()
                if unique_values > 20 or unique_values / len(target) > 0.9:
                    task_type = TaskType.REGRESSION
                else:
                    task_type = TaskType.CLASSIFICATION
        
        # Caractéristiques
        num_samples = len(df)
        num_features = len(df.columns) - (1 if target_column else 0)
        num_numeric = len(df.select_dtypes(include=[np.number]).columns)
        num_categorical = len(df.select_dtypes(include=['object', 'category']).columns)
        
        # Vérifier si c'est des données textuelles (colonnes avec beaucoup de texte)
        has_text_data = False
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].str.len().mean() > 50:
                has_text_data = True
                break
        
        # Vérifier si c'est potentiellement des images (nombreuses colonnes avec valeurs 0-255)
        has_image_data = False
        if num_features > 100 and num_numeric == num_features:
            if df.select_dtypes(include=[np.number]).max().max() <= 255:
                has_image_data = True
        
        return {
            "task_type": task_type.value,
            "num_samples": num_samples,
            "num_features": num_features,
            "num_numeric": num_numeric,
            "num_categorical": num_categorical,
            "has_text_data": has_text_data,
            "has_image_data": has_image_data,
            "sparse": num_numeric == 0,
            "target_column": target_column
        }


class ModelSelector:
    """Sélectionne les modèles les plus adaptés à un dataset"""
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.analyzer = DatasetAnalyzer()
    
    def select_models(
        self,
        dataset_path: str,
        target_column: Optional[str] = None,
        task_type: Optional[str] = None,
        metric: str = "accuracy",
        max_models: int = 5,
        require_gpu: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Sélectionne les modèles les plus adaptés
        
        Args:
            dataset_path: Chemin vers le dataset
            target_column: Colonne cible
            task_type: Type de tâche (classification/regression) - auto-détecté si None
            metric: Métrique à optimiser
            max_models: Nombre maximum de modèles à retourner
            require_gpu: Si True, ne retourne que les modèles nécessitant GPU
        
        Returns:
            Liste des modèles candidats avec scores de compatibilité
        """
        # Analyser le dataset
        dataset_info = self.analyzer.analyze(dataset_path, target_column)
        
        # Utiliser le task_type fourni ou celui détecté
        if task_type:
            dataset_info["task_type"] = task_type.lower()
        
        task_type_enum = TaskType(dataset_info["task_type"])
        
        # Obtenir tous les modèles
        all_models = self.registry.get_all_models()
        
        # Filtrer et scorer les modèles
        candidates = []
        
        for model in all_models:
            # Vérifier la compatibilité de base
            if task_type_enum not in model.task_types:
                continue
            
            if require_gpu and not model.requires_gpu:
                continue
            
            if dataset_info["num_samples"] < model.min_samples:
                continue
            
            if model.max_features and dataset_info["num_features"] > model.max_features:
                continue
            
            # Calculer le score de compatibilité
            score = 0.0
            reasons = []
            
            # Score basé sur le type de données
            if dataset_info["has_text_data"] and model.recommended_for_text:
                score += 2.0
                reasons.append("Recommandé pour données textuelles")
            
            if dataset_info["has_image_data"] and model.recommended_for_images:
                score += 2.0
                reasons.append("Recommandé pour données images")
            
            if not dataset_info["has_text_data"] and not dataset_info["has_image_data"] and model.recommended_for_tabular:
                score += 2.0
                reasons.append("Recommandé pour données tabulaires")
            
            # Score basé sur la taille du dataset
            if dataset_info["num_samples"] >= 10000:
                if model.category == ModelCategory.ENSEMBLE or model.category == ModelCategory.DEEP_LEARNING:
                    score += 1.0
                    reasons.append("Adapté aux gros datasets")
            elif dataset_info["num_samples"] < 1000:
                if model.category == ModelCategory.CLASSICAL:
                    score += 1.0
                    reasons.append("Adapté aux petits datasets")
            
            # Score basé sur le nombre de features
            if dataset_info["num_features"] > 100:
                if model.supports_sparse:
                    score += 0.5
                    reasons.append("Supporte les datasets avec nombreuses features")
            
            # Score basé sur la catégorie (les ensembles sont souvent meilleurs)
            if model.category == ModelCategory.ENSEMBLE:
                score += 1.5
                reasons.append("Modèle d'ensemble performant")
            elif model.category == ModelCategory.CLASSICAL:
                score += 0.5
                reasons.append("Modèle classique rapide")
            
            # Bonus pour XGBoost et RandomForest (généralement très performants)
            if model.name in ["XGBoost", "RandomForest"]:
                score += 1.0
                reasons.append("Modèle très performant pour données tabulaires")
            
            model.compatibility_score = score
            model.reason = "; ".join(reasons) if reasons else "Compatible avec le dataset"
            
            candidates.append(model)
        
        # Trier par score de compatibilité
        candidates.sort(key=lambda x: x.compatibility_score, reverse=True)
        
        # Retourner les top modèles
        return [model.to_dict() for model in candidates[:max_models]]
    
    def get_model_details(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un modèle spécifique"""
        all_models = self.registry.get_all_models()
        for model in all_models:
            if model.name.lower() == model_name.lower():
                return model.to_dict()
        return None
    
    def list_all_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles disponibles"""
        return [model.to_dict() for model in self.registry.get_all_models()]

