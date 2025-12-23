"""
Point d'entrée principal du microservice ModelSelector
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.select import router as select_router

app = FastAPI(
    title="ModelSelector Service",
    description="Microservice de sélection automatique de modèles ML",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routers
app.include_router(select_router, prefix="/api/v1", tags=["select"])


@app.get("/")
def root():
    return {
        "service": "ModelSelector",
        "status": "running",
        "version": "1.0.0",
        "description": "Sélection automatique de modèles d'apprentissage automatique"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/info")
def info():
    """Informations sur le service"""
    from app.core.model_selector import ModelSelector
    selector = ModelSelector()
    models = selector.list_all_models()
    
    return {
        "service": "ModelSelector",
        "total_models": len(models),
        "supported_task_types": ["classification", "regression", "clustering", "time_series"],
        "model_categories": ["classical", "ensemble", "deep_learning", "neural_network"]
    }

