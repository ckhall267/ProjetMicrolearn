"""
API endpoints pour la sélection de modèles
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.model_selector import ModelSelector
from app.core.database import save_model_selection, get_model_selection
from app.core.minio_client import download_file_from_minio
import os

router = APIRouter()
model_selector = ModelSelector()


class SelectRequest(BaseModel):
    """Requête pour sélectionner des modèles"""
    dataset_id: str
    dataset_path: str
    target_column: Optional[str] = None
    task_type: Optional[str] = None  # classification, regression, etc.
    metric: str = "accuracy"
    max_models: int = 5
    require_gpu: bool = False


class SelectResponse(BaseModel):
    """Réponse de sélection de modèles"""
    dataset_id: str
    task_type: str
    metric: str
    selected_models: List[Dict[str, Any]]
    total_models_evaluated: int


@router.post("/select", response_model=SelectResponse)
def select_models(request: SelectRequest):
    """
    Sélectionne les modèles les plus adaptés pour un dataset
    
    Args:
        request: Requête contenant les informations du dataset
    
    Returns:
        Liste des modèles sélectionnés avec leurs scores de compatibilité
    """
    try:
        # Télécharger le dataset depuis MinIO si nécessaire
        if request.dataset_path.startswith("s3://") or "/" in request.dataset_path:
            local_dataset_path = download_file_from_minio(request.dataset_path)
        else:
            # Supposer que c'est un chemin local
            local_dataset_path = request.dataset_path
            if not os.path.exists(local_dataset_path):
                raise HTTPException(
                    status_code=404,
                    detail=f"Dataset non trouvé: {local_dataset_path}"
                )
        
        # Sélectionner les modèles
        selected_models = model_selector.select_models(
            dataset_path=local_dataset_path,
            target_column=request.target_column,
            task_type=request.task_type,
            metric=request.metric,
            max_models=request.max_models,
            require_gpu=request.require_gpu
        )
        
        # Sauvegarder la sélection dans la base de données
        save_model_selection(
            dataset_id=request.dataset_id,
            dataset_path=request.dataset_path,
            task_type=request.task_type or "auto",
            metric=request.metric,
            selected_models=selected_models,
            config={
                "max_models": request.max_models,
                "require_gpu": request.require_gpu,
                "target_column": request.target_column
            }
        )
        
        # Nettoyer le fichier temporaire
        if local_dataset_path != request.dataset_path and os.path.exists(local_dataset_path):
            os.remove(local_dataset_path)
        
        return SelectResponse(
            dataset_id=request.dataset_id,
            task_type=request.task_type or "auto",
            metric=request.metric,
            selected_models=selected_models,
            total_models_evaluated=len(selected_models)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la sélection de modèles: {str(e)}"
        )


@router.get("/select")
def select_models_get(
    dataset_id: str = Query(..., description="ID du dataset"),
    dataset_path: str = Query(..., description="Chemin du dataset dans MinIO"),
    target_column: Optional[str] = Query(None, description="Colonne cible"),
    task_type: Optional[str] = Query(None, description="Type de tâche (classification/regression)"),
    metric: str = Query("accuracy", description="Métrique à optimiser"),
    max_models: int = Query(5, description="Nombre maximum de modèles à retourner"),
    require_gpu: bool = Query(False, description="Nécessite GPU")
):
    """
    Endpoint GET pour sélectionner des modèles (alternative à POST)
    """
    request = SelectRequest(
        dataset_id=dataset_id,
        dataset_path=dataset_path,
        target_column=target_column,
        task_type=task_type,
        metric=metric,
        max_models=max_models,
        require_gpu=require_gpu
    )
    return select_models(request)


@router.get("/select/{dataset_id}/history")
def get_selection_history(dataset_id: str):
    """
    Récupère l'historique des sélections de modèles pour un dataset
    """
    try:
        history = get_model_selection(dataset_id)
        return {
            "dataset_id": dataset_id,
            "history": history
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )


@router.get("/models")
def list_all_models():
    """
    Liste tous les modèles disponibles dans le registre
    """
    try:
        models = model_selector.list_all_models()
        return {
            "total_models": len(models),
            "models": models
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des modèles: {str(e)}"
        )


@router.get("/models/{model_name}")
def get_model_details(model_name: str):
    """
    Récupère les détails d'un modèle spécifique
    """
    try:
        model = model_selector.get_model_details(model_name)
        if not model:
            raise HTTPException(
                status_code=404,
                detail=f"Modèle non trouvé: {model_name}"
            )
        return model
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération du modèle: {str(e)}"
        )

