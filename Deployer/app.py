from flask import Flask, request, jsonify
import os
import io
import joblib
import pandas as pd
from minio import Minio

app = Flask(__name__)

# --- Configuration MinIO ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "microlearn-data")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Cache simple en mémoire pour ne pas recharger le modèle à chaque requête
# Structure: { "model_id": { "model": object, "last_accessed": timestamp } }
GLOBAL_MODEL_CACHE = {}

@app.route('/')
def home():
    return jsonify({"service": "Deployer", "status": "active"})

@app.route('/deploy', methods=['POST'])
def deploy_model():
    """
    Enregistre logiquement un déploiement (peut juste vérifier que le modèle existe sur MinIO)
    """
    data = request.json
    model_id = data.get("model_id")
    
    if not model_id:
        return jsonify({"error": "model_id is required"}), 400
    
    # Vérifier l'existence sur MinIO
    try:
        minio_client.stat_object(MINIO_BUCKET, f"models/{model_id}.joblib")
    except Exception as e:
         return jsonify({"error": f"Model not found in storage: {str(e)}"}), 404

    endpoint = f"/predict/{model_id}"
    
    return jsonify({
        "status": "ready",
        "deployment_id": f"dep_{model_id}",
        "endpoint": endpoint,
        "message": f"Model {model_id} is ready for inference"
    })

@app.route('/predict/<model_id>', methods=['POST'])
def predict(model_id):
    try:
        # 1. Charger le modèle (Cache ou MinIO)
        if model_id not in GLOBAL_MODEL_CACHE:
            print(f"Loading model {model_id} from MinIO...")
            try:
                response = minio_client.get_object(MINIO_BUCKET, f"models/{model_id}.joblib")
                model_buffer = io.BytesIO(response.read())
                model = joblib.load(model_buffer)
                GLOBAL_MODEL_CACHE[model_id] = model
            except Exception as e:
                return jsonify({"error": f"Failed to load model: {str(e)}"}), 500
        else:
             model = GLOBAL_MODEL_CACHE[model_id]

        # 2. Préparer les données
        input_data = request.json
        # Support single instance (dict) or batch (list)
        if isinstance(input_data, dict):
            df = pd.DataFrame([input_data])
        elif isinstance(input_data, list):
            df = pd.DataFrame(input_data)
        else:
            return jsonify({"error": "Invalid input format. Expected JSON dict or list"}), 400
        
        # Encodage basique (One-Hot) - Attention: doit matcher l'entraînement !
        # Idéalement, le pipeline de transformation (ColumnTransformer) devrait être sauvé AVEC le modèle.
        # Ici on fait au mieux.
        df = pd.get_dummies(df) 
        
        # Alignement des colonnes (si le modèle attend des colonnes spécifiques)
        # TODO: Gérer l'alignement strict

        # 3. Prédiction
        prediction = model.predict(df)
        
        return jsonify({
            "model_id": model_id,
            "prediction": prediction.tolist()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
