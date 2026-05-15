# from fastapi import FastAPI, Request, HTTPException
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from slowapi import _rate_limit_exceeded_handler
# from slowapi.errors import RateLimitExceeded
# from app.core.limiter import limiter
# import os

# #from fastapi.exceptions import RequestValidationError
# #from fastapi.responses import JSONResponse

# from app.api.v1 import api_router
# from app.config import settings
# from app.core.logging_config import setup_logging

# setup_logging()

# app = FastAPI(
#     title=settings.APP_NAME,
#     description="A course enrollment platform with JWT authentication",
#     version="1.0.0"
# )
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.include_router(api_router, prefix="/api/v1")
# # Create uploads directory if it doesn't exist
# os.makedirs("uploads", exist_ok=True)


# # Mount static files for frontend and uploads
# app.mount("/static", StaticFiles(directory="frontend"), name="static")
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
# a

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter
import os

from app.api.v1 import api_router
from app.config import settings
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="A course enrollment platform with JWT authentication",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

#  API routes FIRST
app.include_router(api_router, prefix="/api/v1")

#  Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

#  Uploads (only once)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Static assets
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Frontend LAST
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")