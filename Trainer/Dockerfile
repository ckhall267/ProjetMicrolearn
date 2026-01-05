FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for Ray or PyTorch if needed (minimal here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
# Splitting heavy installs to avoid timeouts
RUN pip install --default-timeout=1000 --no-cache-dir torch
RUN pip install --default-timeout=1000 --no-cache-dir pytorch-lightning
RUN pip install --default-timeout=1000 --no-cache-dir ray[default]
RUN pip install --default-timeout=1000 --no-cache-dir -r /app/requirements.txt

COPY app /app/app
# Note: copying 'app' folder content into '/app/app' to match import structure 'from app.api...'
# OR better: COPY app /app/app and set PYTHONPATH or stick to structure.
# DataPreparer did: COPY app /app. And CMD ["uvicorn", "main:app"...]
# But DataPreparer imports `from app.api...`. If /app is WORKDIR, then /app/app exists.
# Let's match DataPreparer:
# WORKDIR /app
# COPY app /app
# This puts main.py at /app/main.py ? No.
# If local is DataPreparer/app/main.py.
# COPY app /app -> /app/main.py (if app/ has main.py at root).
# Wait, DataPreparer structure:
# DataPreparer/
#   app/
#     main.py
# If I do `COPY app /app`, then inside container /app has main.py.
# Correct.

COPY app /app/app
 
EXPOSE 8002
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
