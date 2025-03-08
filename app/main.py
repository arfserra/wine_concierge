from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api")

# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)

# Set up static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Web routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/collection.html", response_class=HTMLResponse)
async def collection(request: Request):
    return templates.TemplateResponse("collection.html", {"request": request})

@app.get("/storage.html", response_class=HTMLResponse)
async def storage(request: Request):
    return templates.TemplateResponse("storage.html", {"request": request})

@app.get("/add-wine.html", response_class=HTMLResponse)
async def add_wine(request: Request):
    return templates.TemplateResponse("add-wine.html", {"request": request})

@app.get("/pairing.html", response_class=HTMLResponse)
async def pairing(request: Request):
    return templates.TemplateResponse("pairing.html", {"request": request})