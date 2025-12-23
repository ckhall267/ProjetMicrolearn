FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le code de l'application
COPY app /app

# Exposer le port
EXPOSE 8001

# Commande pour démarrer le service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

