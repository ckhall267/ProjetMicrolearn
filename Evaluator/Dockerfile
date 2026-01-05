FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install --default-timeout=1000 --no-cache-dir -r /app/requirements.txt

COPY app /app/app

EXPOSE 8003
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
