from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.prepare import router as prepare_router

app = FastAPI(title="DataPreparer Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prepare_router, prefix="/api/v1", tags=["prepare"])

@app.get("/")
def root():
    return {"service": "DataPreparer", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
