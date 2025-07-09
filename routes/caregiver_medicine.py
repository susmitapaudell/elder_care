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


# Directory to store user data
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_db_path(user_id: str):
    return Path(DATA_DIR) / f"{user_id}_data.json"

def load_user_data(user_id: str):
    db_path = get_user_db_path(user_id)
    if db_path.exists():
        with open(db_path, 'r') as f:
            return json.load(f)
    return {
        "medicines": [],
        "tracking": {}
    }

def save_user_data(user_id: str, data: dict):
    db_path = get_user_db_path(user_id)
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("/{user_id}/medicine", response_class=HTMLResponse)
async def medicine_page(request: Request, user_id: str):
    if not (user_id.isdigit() and len(user_id) == 4):
        raise HTTPException(status_code=404, detail="User ID must be 4 digits")
    
    # Load user data to pass to template
    user_data = load_user_data(user_id)
    return templates.TemplateResponse("caregiver_medicine.html", {
        "request": request,
        "user_id": user_id,
        "initial_data": user_data
    })

@router.post("/{user_id}/save_medicine")
async def save_medicine(user_id: str, request: Request):
    data = await request.json()
    user_data = load_user_data(user_id)
    
    # Update medicines list
    if 'medicines' in data:
        user_data['medicines'] = data['medicines']
    
    # Update tracking data
    if 'tracking' in data:
        user_data['tracking'] = data['tracking']
    
    save_user_data(user_id, user_data)
    return JSONResponse({"status": "success"})

@router.get("/{user_id}/load_medicine")
async def load_medicine(user_id: str):
    return JSONResponse(load_user_data(user_id))