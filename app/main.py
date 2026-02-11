from fastapi import FastAPI
from app.api.v1 import api_router
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A course enrollment platform with JWT authentication",
    version="1.0.0"
)


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to Course Enrollment Platform",
    }
