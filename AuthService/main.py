from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import engine, Base
import models

# Création des tables si elles n'existent pas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroLearn Auth Service")

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Welcome to MicroLearn Auth Service (Connected to PostgreSQL)"}
