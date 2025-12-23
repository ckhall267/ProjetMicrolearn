from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.train import router as train_router

app = FastAPI(title="Trainer Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(train_router, prefix="/api/v1", tags=["train"])

@app.get("/")
def root():
    return {"service": "Trainer", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
