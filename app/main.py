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

# # Create uploads directory if it doesn't exist
# os.makedirs("uploads", exist_ok=True)


# # Mount static files for frontend and uploads
# app.mount("/static", StaticFiles(directory="frontend"), name="static")
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
# app.include_router(api_router, prefix="/api/v1")






# @app.get("/{full_path:path}")
# async def serve_frontend(full_path: str):
#     # If the path starts with api/v1 or uploads, let them be handled by their respective routers/mounts
#     if full_path.startswith("api/v1") or full_path.startswith("uploads"):
#         raise HTTPException(status_code=404)
        
#     # Otherwise, serve the index.html for SPA routing
#     return FileResponse("frontend/index.html")


# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
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

# ✅ API routes FIRST
app.include_router(api_router, prefix="/api/v1")

# ✅ Uploads mount
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Health check BEFORE the frontend mount
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ✅ Frontend mount LAST — catches everything else
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")