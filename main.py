from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from router.api import router

swagger_docs = "docs"
redoc_docs = "redoc"

app = FastAPI(
    debug=True,
    docs_url=f"/{swagger_docs}" if swagger_docs else None,
    redoc_url=f"/{redoc_docs}" if redoc_docs else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)