
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
from api.hyperv_routes import router as hyperv_router
from api.workload_routes import router as workload_router

app = FastAPI(title="IROA - Intelligent Resource Optimization Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "*"  # Allow all origins as fallback
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "*",
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
)

app.include_router(api_router)
app.include_router(hyperv_router)
app.include_router(workload_router, prefix="/workload")

@app.get("/health")
def health_check():
    return {"status": "ok"}
