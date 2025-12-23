from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)

MODELS_DIR = os.getenv("MODELS_DIR", "./models")

@app.route('/')
def home():
    return jsonify({"service": "Deployer", "status": "active"})

@app.route('/deploy', methods=['POST'])
def deploy_model():
    """
    Simule le déploiement d'un modèle.
    Dans une vraie implémentation, ceci lancerait un container Docker avec TorchServe.
    """
    data = request.json
    model_id = data.get("model_id")
    deployment_type = data.get("type", "rest")
    
    if not model_id:
        return jsonify({"error": "model_id is required"}), 400
        
    # Simulation de la logique de déploiement
    deployment_id = f"dep_{model_id}_{deployment_type}"
    endpoint = f"http://localhost:8080/predictions/{model_id}"
    
    return jsonify({
        "status": "deployed",
        "deployment_id": deployment_id,
        "endpoint": endpoint,
        "message": f"Model {model_id} successfully deployed as {deployment_type}"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
