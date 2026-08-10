from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise Edge ANPR, Gate Automation and Vehicle Trip Management Platform API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.endpoints.benchmark import router as benchmark_router

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(benchmark_router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "online", "system": "Edge ANPR & Trip Management Platform"}


@app.get("/api/system/health", tags=["Health"])
def api_system_health():
    from app.ai.inference.backend_selector import get_active_backend_info
    return get_active_backend_info()