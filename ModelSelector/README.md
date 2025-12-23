# ModelSelector - Microservice de Sélection de Modèles

## Description

ModelSelector est le deuxième microservice de la plateforme MicroLearn. Il analyse automatiquement les datasets et recommande les modèles d'apprentissage automatique les plus adaptés en fonction des caractéristiques des données.

## Fonctionnalités

- **Analyse automatique des datasets** : Détection du type de tâche (classification/régression), caractéristiques des données
- **Sélection intelligente de modèles** : Recommandation basée sur la compatibilité modèle/dataset
- **Registre de modèles** : Catalogue de plus de 14 modèles (XGBoost, RandomForest, SVM, CNN, LSTM, etc.)
- **Scoring de compatibilité** : Score de compatibilité pour chaque modèle recommandé
- **Historique** : Sauvegarde des sélections dans PostgreSQL

## Technologies

- **Python 3.11**
- **FastAPI** : Framework web asynchrone
- **Pandas** : Analyse de données
- **scikit-learn** : Bibliothèque ML
- **PostgreSQL** : Base de données
- **MinIO** : Stockage objet pour les datasets

## Installation

### Prérequis

- Docker et Docker Compose
- Python 3.11+ (pour développement local)

### Avec Docker

```bash
cd ModelSelector
docker-compose up -d
```

Le service sera accessible sur `http://localhost:8001`

### Développement local

```bash
cd ModelSelector/app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### POST `/api/v1/select`

Sélectionne les modèles les plus adaptés pour un dataset.

**Requête :**
```json
{
  "dataset_id": "dataset_123",
  "dataset_path": "microlearn-data/datasets/dataset.csv",
  "target_column": "target",
  "task_type": "classification",
  "metric": "accuracy",
  "max_models": 5,
  "require_gpu": false
}
```

**Réponse :**
```json
{
  "dataset_id": "dataset_123",
  "task_type": "classification",
  "metric": "accuracy",
  "selected_models": [
    {
      "name": "XGBoost",
      "category": "ensemble",
      "compatibility_score": 6.5,
      "reason": "Modèle très performant pour données tabulaires; Adapté aux gros datasets",
      "task_types": ["classification", "regression"],
      "hyperparameters": {...}
    }
  ],
  "total_models_evaluated": 5
}
```

### GET `/api/v1/models`

Liste tous les modèles disponibles dans le registre.

### GET `/api/v1/models/{model_name}`

Récupère les détails d'un modèle spécifique.

### GET `/api/v1/select/{dataset_id}/history`

Récupère l'historique des sélections pour un dataset.

## Modèles supportés

### Modèles classiques
- Logistic Regression
- Decision Tree
- K-Nearest Neighbors
- Naive Bayes
- Linear Regression
- Ridge
- Lasso

### Modèles d'ensemble
- XGBoost
- Random Forest
- Gradient Boosting
- AdaBoost

### Deep Learning
- CNN (Convolutional Neural Network)
- LSTM (Long Short-Term Memory)

### Autres
- SVM (Support Vector Machine)

## Configuration

Les variables d'environnement peuvent être configurées dans `docker-compose.yml` :

- `DATABASE_URL` : URL de connexion PostgreSQL
- `MINIO_ENDPOINT` : Endpoint MinIO
- `MINIO_ACCESS_KEY` : Clé d'accès MinIO
- `MINIO_SECRET_KEY` : Clé secrète MinIO
- `MINIO_BUCKET` : Nom du bucket MinIO

## Structure du projet

```
ModelSelector/
├── app/
│   ├── api/
│   │   └── select.py          # Endpoints API
│   ├── core/
│   │   ├── model_selector.py  # Logique de sélection
│   │   ├── database.py        # Gestion PostgreSQL
│   │   └── minio_client.py    # Client MinIO
│   ├── main.py                # Point d'entrée FastAPI
│   └── requirements.txt       # Dépendances Python
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Intégration avec les autres microservices

- **DataPreparer** : Utilise les datasets préparés stockés dans MinIO
- **Trainer** (futur) : Fournit la liste des modèles à entraîner
- **Orchestrator** (futur) : Reçoit les demandes d'orchestration de pipeline

## Tests

```bash
# Tests manuels avec curl
curl -X POST http://localhost:8001/api/v1/select \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "test_dataset",
    "dataset_path": "microlearn-data/datasets/test.csv",
    "task_type": "classification",
    "max_models": 5
  }'
```

## Documentation API

Une fois le service démarré, accédez à la documentation interactive :
- Swagger UI : `http://localhost:8001/docs`
- ReDoc : `http://localhost:8001/redoc`

