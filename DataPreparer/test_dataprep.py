import requests
import json

# URL de l'API DataPreparer (locale)
url = "http://localhost:8002/api/v1/prepare"

# Charge utile (Payload) de la requête
# Assurez-vous d'avoir uploadé un fichier 'data.csv' dans le bucket 'microlearn-data' sur MinIO
payload = {
    # Chemin vers le fichier dans MinIO
    "file_path": "microlearn-data/AmesHousing.csv",
    
    # Pipeline de nettoyage à appliquer
    "pipeline": {
        "steps": [
            {
                "name": "Validation",
                "method": "check_missing"
            },
            {
                "name": "Imputation", 
                "method": "mean" # Remplace les trous par la moyenne
            }
        ]
    },
    "dataset_id": "test_dataset_001"
}

print(f"Envoi de la requête à {url}...")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ SUCCÈS !")
        print("Réponse du serveur :")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ ERREUR (Code {response.status_code})")
        print(response.text)

except Exception as e:
    print(f"\n❌ IMPOSSIBLE DE CONNECTER AU SERVEUR : {e}")
    print("Vérifiez que le service DataPreparer tourne sur le port 8002.")
