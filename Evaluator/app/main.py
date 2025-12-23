from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.evaluate import router as eval_router

app = FastAPI(title="Evaluator Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(eval_router, prefix="/api/v1", tags=["evaluate"])

@app.get("/")
def root():
    return {"service": "Evaluator", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
