import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from xknxmono.catalog.routers import catalog_sections, hardware, manufacturers, upload

app = FastAPI(
    title="XKNX Toolkit Catalog API",
    description="REST API for browsing the XKNX Toolkit catalog.",
    version="0.1.0",
    servers=[{"url": "http://localhost:8000", "description": "Local dev server"}],
    openapi_tags=[
        {"name": "Hardware", "description": "KNX hardware listings and application details."},
        {"name": "Manufacturers", "description": "KNX manufacturer directory."},
        {"name": "Upload", "description": "Upload .knxprod files into the catalog."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(manufacturers.router)
app.include_router(hardware.router)
app.include_router(catalog_sections.router)
app.include_router(upload.router)


def main():
    uvicorn.run("xknxmono.catalog.app:app", host="0.0.0.0", port=8000, reload=True)
