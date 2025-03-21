from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import os
from typing import List, Optional
import json
import uuid
from datetime import datetime

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up uploads directory for wine labels
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Mock data for storage
STORAGE_DATA = []

# Mock data for wines
WINE_DATA = []

# Web routes for pages
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/collection")
async def collection(request: Request):
    return templates.TemplateResponse("collection.html", {"request": request})

@app.get("/storage")
async def storage(request: Request):
    return templates.TemplateResponse("storage.html", {"request": request})

@app.get("/add-wine")
async def add_wine(request: Request):
    return templates.TemplateResponse("add-wine.html", {"request": request})

# API Routes for storage
@app.get("/api/storage")
async def get_storage_units():
    return STORAGE_DATA

@app.get("/api/storage/{storage_id}")
async def get_storage_by_id(storage_id: str):
    for storage in STORAGE_DATA:
        if storage["id"] == storage_id:
            return storage
    raise HTTPException(status_code=404, detail="Storage not found")

@app.post("/api/storage")
async def create_storage(storage: dict):
    storage_id = str(uuid.uuid4())
    new_storage = {
        "id": storage_id,
        **storage
    }
    STORAGE_DATA.append(new_storage)
    return new_storage

@app.put("/api/storage/{storage_id}")
async def update_storage(storage_id: str, storage_data: dict):
    for i, storage in enumerate(STORAGE_DATA):
        if storage["id"] == storage_id:
            STORAGE_DATA[i] = {
                "id": storage_id,
                **storage_data
            }
            return STORAGE_DATA[i]
    raise HTTPException(status_code=404, detail="Storage not found")

@app.delete("/api/storage/{storage_id}")
async def delete_storage(storage_id: str):
    for i, storage in enumerate(STORAGE_DATA):
        if storage["id"] == storage_id:
            del STORAGE_DATA[i]
            return {"success": True}
    raise HTTPException(status_code=404, detail="Storage not found")

# API Routes for wines
@app.get("/api/wines")
async def get_wines(storage_id: Optional[str] = None):
    if storage_id:
        return [wine for wine in WINE_DATA if wine["storage_id"] == storage_id]
    return WINE_DATA

@app.get("/api/wines/{wine_id}")
async def get_wine_by_id(wine_id: str):
    for wine in WINE_DATA:
        if wine["id"] == wine_id:
            return wine
    raise HTTPException(status_code=404, detail="Wine not found")

@app.post("/api/wines")
async def add_wine(wine_data: str = Form(...), label_image: Optional[UploadFile] = None):
    try:
        wine_dict = json.loads(wine_data)
        wine_id = str(uuid.uuid4())
        
        # Handle image upload if provided
        label_image_url = None
        if label_image:
            # Create a unique filename
            filename = f"{uuid.uuid4()}{os.path.splitext(label_image.filename)[1]}"
            file_path = os.path.join("uploads", filename)
            
            # Save the file
            with open(file_path, "wb") as buffer:
                content = await label_image.read()
                buffer.write(content)
            
            label_image_url = filename
        
        # Create the wine entry
        new_wine = {
            "id": wine_id,
            "added_date": datetime.now().isoformat(),
            "label_image_url": label_image_url,
            **wine_dict
        }
        
        WINE_DATA.append(new_wine)
        return new_wine
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in wine_data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wines/analyze")
async def analyze_wine_label(label_image: UploadFile = File(...)):
    try:
        # Save the uploaded image
        filename = f"{uuid.uuid4()}{os.path.splitext(label_image.filename)[1]}"
        file_path = os.path.join("uploads", filename)
        
        with open(file_path, "wb") as buffer:
            content = await label_image.read()
            buffer.write(content)
        
        # Mock analysis results - in a real app, you'd call OpenAI here
        analysis_result = {
            "success": True,
            "key_info": {
                "name": "Sample Wine",
                "producer": "Test Winery",
                "vintage": 2019,
                "type": "Red",
                "region": "Test Region",
                "country": "Test Country",
                "varietal": ["Cabernet Sauvignon"]
            },
            "description": "A delicious full-bodied red wine with notes of black cherry and vanilla.",
            "label_image_url": filename
        }
        
        return analysis_result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.put("/api/wines/{wine_id}")
async def update_wine(wine_id: str, wine_data: dict):
    for i, wine in enumerate(WINE_DATA):
        if wine["id"] == wine_id:
            WINE_DATA[i] = {
                **wine,
                **wine_data
            }
            return WINE_DATA[i]
    raise HTTPException(status_code=404, detail="Wine not found")

@app.delete("/api/wines/{wine_id}")
async def delete_wine(wine_id: str):
    for i, wine in enumerate(WINE_DATA):
        if wine["id"] == wine_id:
            del WINE_DATA[i]
            return {"success": True}
    raise HTTPException(status_code=404, detail="Wine not found")

# Sample data initialization
def init_sample_data():
    # Sample storage
    sample_storage = {
        "id": "sample-storage-1",
        "name": "Living Room Wine Rack",
        "type": "Wine Rack",
        "position_naming_scheme": "Row-Column",
        "zones": [
            {
                "name": "Main Zone",
                "dimensions": {
                    "rows": 4,
                    "columns": 6
                }
            }
        ],
        "total_positions": 24
    }
    
    STORAGE_DATA.append(sample_storage)
    
    # Sample wine
    sample_wine = {
        "id": "sample-wine-1",
        "name": "Chateau Sample",
        "producer": "Sample Winery",
        "vintage": 2019,
        "type": "Red",
        "region": "Bordeaux",
        "country": "France",
        "storage_id": "sample-storage-1",
        "position": "1A",
        "added_date": datetime.now().isoformat(),
        "description": "A wonderful red wine with notes of black fruits and oak."
    }
    
    WINE_DATA.append(sample_wine)

# Initialize sample data
init_sample_data()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)