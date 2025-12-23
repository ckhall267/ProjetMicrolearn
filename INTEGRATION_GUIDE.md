# Guide d'intégration - MicroLearn

## Vue d'ensemble

Ce document décrit l'intégration des microservices DataPreparer et ModelSelector dans la plateforme MicroLearn.

## Services implémentés

### 1. DataPreparer (Port 8000)

**Statut** : ✅ Complété et amélioré

**Fonctionnalités** :
- Nettoyage de données (imputation, scaling, encoding)
- Support CSV et JSON
- Intégration MinIO pour le stockage
- Base de données PostgreSQL pour les métadonnées
- API REST complète

**Améliorations apportées** :
- Correction des imports et structure
- Client MinIO amélioré avec gestion d'erreurs
- Pipeline de transformation enrichi
- API structurée avec FastAPI routers
- Gestion de base de données complète

**Endpoints** :
- `POST /api/v1/prepare` - Préparer un dataset
- `GET /api/v1/prepare/{dataset_id}` - Récupérer un dataset préparé

### 2. ModelSelector (Port 8001)

**Statut** : ✅ Nouvellement créé

**Fonctionnalités** :
- Analyse automatique des datasets
- Sélection intelligente de modèles (14+ modèles supportés)
- Scoring de compatibilité modèle/dataset
- Historique des sélections
- Catalogue de modèles

**Modèles supportés** :
- **Classiques** : Logistic Regression, Decision Tree, KNN, Naive Bayes, Linear/Ridge/Lasso Regression
- **Ensemble** : XGBoost, Random Forest, Gradient Boosting, AdaBoost
- **Deep Learning** : CNN, LSTM
- **Autres** : SVM

**Endpoints** :
- `POST /api/v1/select` - Sélectionner des modèles
- `GET /api/v1/models` - Lister tous les modèles
- `GET /api/v1/models/{model_name}` - Détails d'un modèle
- `GET /api/v1/select/{dataset_id}/history` - Historique de sélection

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│ DataPreparer │────────▶│ MinIO       │
│  (React)    │         │   :8000      │         │  :9000      │
└─────────────┘         └──────────────┘         └─────────────┘
       │                       │
       │                       ▼
       │                 ┌─────────────┐
       │                 │ PostgreSQL  │
       │                 │   :5432     │
       │                 └─────────────┘
       │
       ▼
┌──────────────┐         ┌─────────────┐
│ ModelSelector│────────▶│ MinIO       │
│   :8001      │         │  :9000      │
└──────────────┘         └─────────────┘
       │
       ▼
┌─────────────┐
│ PostgreSQL  │
│   :5432     │
└─────────────┘
```

## Installation et démarrage

### Prérequis
- Docker et Docker Compose
- Node.js 16+ (pour le frontend)

### Démarrage des services

#### 1. DataPreparer
```bash
cd DataPreparer
docker-compose up -d
```

#### 2. ModelSelector
```bash
cd ModelSelector
docker-compose up -d
```

#### 3. Frontend
```bash
cd microlearn-frontend
npm install
npm start
```

## Configuration des services

### Variables d'environnement communes

**PostgreSQL** :
- Host: `localhost:5432`
- Database: `microlearn`
- User: `mluser`
- Password: `mlpass`

**MinIO** :
- Endpoint: `localhost:9000`
- Access Key: `minio`
- Secret Key: `minio123`
- Bucket: `microlearn-data`

### Ports

- DataPreparer: `8000`
- ModelSelector: `8001`
- PostgreSQL: `5432`
- MinIO: `9000` (API), `9001` (Console)
- Frontend: `3000`

## Workflow d'utilisation

### 1. Préparation des données (DataPreparer)

```bash
curl -X POST http://localhost:8000/api/v1/prepare \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "microlearn-data/datasets/raw_data.csv",
    "dataset_id": "dataset_001",
    "pipeline": {
      "steps": [
        {
          "name": "imputation",
          "strategy": "mean"
        },
        {
          "name": "one_hot_encoding",
          "columns": ["category"]
        },
        {
          "name": "scaling",
          "method": "standard"
        }
      ]
    }
  }'
```

### 2. Sélection de modèles (ModelSelector)

```bash
curl -X POST http://localhost:8001/api/v1/select \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "dataset_001",
    "dataset_path": "microlearn-data/cleaned/dataset_001.csv",
    "target_column": "target",
    "task_type": "classification",
    "metric": "accuracy",
    "max_models": 5
  }'
```

### 3. Interface web

1. Accéder à `http://localhost:3000`
2. Uploader un dataset via `/upload`
3. Configurer le pipeline AutoML via `/automl`
4. Voir les modèles recommandés via `/model-selector`
5. Consulter les résultats via `/dashboard`

## Intégration Frontend

### Pages ajoutées/modifiées

1. **AutoML** (`/automl`) - Intégration de ModelSelector
   - Sélection automatique de modèles
   - Affichage des scores de compatibilité
   - Configuration du pipeline

2. **ModelSelector** (`/model-selector`) - Nouvelle page
   - Interface dédiée à la sélection de modèles
   - Vue détaillée des modèles recommandés
   - Catalogue complet des modèles disponibles

### Variables d'environnement Frontend

Créez un fichier `.env` dans `microlearn-frontend/` :

```env
REACT_APP_DATAPREPARER_API=http://localhost:8000/api/v1
REACT_APP_MODEL_SELECTOR_API=http://localhost:8001/api/v1
```

## Base de données

### Tables créées

**DataPreparer** :
- `prepared_datasets` - Métadonnées des datasets préparés

**ModelSelector** :
- `model_catalogue` - Catalogue des modèles
- `model_selections` - Historique des sélections
- `model_compatibilities` - Cache des compatibilités

Les tables sont créées automatiquement au démarrage des services.

## Prochaines étapes

### Microservices à développer

1. **Trainer** - Entraînement des modèles
2. **Evaluator** - Évaluation des performances
3. **HyperOpt** - Optimisation des hyperparamètres
4. **Deployer** - Déploiement des modèles
5. **Orchestrator** - Orchestration du pipeline complet

### Améliorations possibles

- Authentification et autorisation
- Gestion des erreurs plus robuste
- Tests unitaires et d'intégration
- Monitoring et logging (Prometheus, Grafana)
- Documentation API plus complète
- Support de plus de formats de données

## Support

Pour toute question ou problème :
- Consulter les README.md de chaque microservice
- Vérifier les logs Docker : `docker-compose logs -f [service_name]`
- Accéder à la documentation Swagger : `http://localhost:8000/docs` ou `http://localhost:8001/docs`

