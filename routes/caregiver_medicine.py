from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path
from datetime import datetime

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# Database configuration
DATABASE_DIR = "medicine_database"
DATA_FILE = "default_data.json"
DATABASE_PATH = Path(DATABASE_DIR) / DATA_FILE

# Ensure database directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

def load_data():
    if DATABASE_PATH.exists():
        with open(DATABASE_PATH, 'r') as f:
            return json.load(f)
    return {
        "medicines": [],
        "tracking": {}
    }

def save_data(data: dict):
    with open(DATABASE_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("/caregiver/medicine", response_class=HTMLResponse)
async def medicine_page(request: Request):
    # Load data from default file
    medicine_data = load_data()
    return templates.TemplateResponse("caregiver_medicine.html", {
        "request": request,
        "initial_data": medicine_data
    })

@router.post("/caregiver/save_medicine")
async def save_medicine(request: Request):
    data = await request.json()
    current_data = load_data()
    
    # Update medicines list
    if 'medicines' in data:
        current_data['medicines'] = data['medicines']
    
    # Update tracking data
    if 'tracking' in data:
        current_data['tracking'] = data['tracking']
    
    save_data(current_data)
    print(f"✅ Saved to {DATABASE_PATH}")
    return JSONResponse({"status": "success"})

@router.get("/caregiver/load_medicine")
async def load_medicine():
    return JSONResponse(load_data())