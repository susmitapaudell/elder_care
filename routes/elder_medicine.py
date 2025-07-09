from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import os
from pathlib import Path
from datetime import datetime, date

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
            data = json.load(f)
            # Ensure the data structure is correct
            if 'medicines' not in data:
                data['medicines'] = []
            if 'tracking' not in data:
                data['tracking'] = {}
            return data
    return {
        "medicines": [],
        "tracking": {}
    }

def save_user_data(user_id: str, data: dict):
    db_path = get_user_db_path(user_id)
    with open(db_path, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("/elder/{user_id}/medicine", response_class=HTMLResponse)
async def medicine_page(request: Request, user_id: str):
    if not (user_id.isdigit() and len(user_id) == 4):
        raise HTTPException(status_code=404, detail="User ID must be 4 digits")
    
    user_data = load_user_data(user_id)
    
    # Add today's date to the context
    today = date.today().isoformat()
    
    return templates.TemplateResponse("elder_medicine.html", {
        "request": request,
        "user_id": user_id,
        "initial_data": user_data,
        "today": today
    })

@router.post("/elder/{user_id}/save_medicine")
async def save_medicine(user_id: str, request: Request):
    try:
        data = await request.json()
        user_data = load_user_data(user_id)
        
        # Validate and update medicines list
        if 'medicines' in data:
            if not isinstance(data['medicines'], list):
                raise HTTPException(status_code=400, detail="Medicines must be a list")
            user_data['medicines'] = data['medicines']
        
        # Validate and update tracking data
        if 'tracking' in data:
            if not isinstance(data['tracking'], dict):
                raise HTTPException(status_code=400, detail="Tracking must be a dictionary")
            
            # Merge new tracking data with existing
            for key, value in data['tracking'].items():
                # Validate tracking entry structure
                if not isinstance(value, dict):
                    continue
                if 'taken' not in value:
                    continue
                
                # If the medicine was taken but no actual time provided, use scheduled time
                if value['taken'] and 'actualTime' not in value:
                    # Extract time from the key (format: medicineName_date_time)
                    parts = key.split('_')
                    if len(parts) >= 3:
                        value['actualTime'] = parts[-1]  # Use the scheduled time
        
            user_data['tracking'].update(data['tracking'])
        
        save_user_data(user_id, user_data)
        print(f"✅ Saved data for user {user_id}")
        return JSONResponse({"status": "success", "message": "Data saved successfully"})
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/elder/{user_id}/load_medicine")
async def load_medicine(user_id: str):
    try:
        user_data = load_user_data(user_id)
        
        # Add today's date to the response
        today = date.today().isoformat()
        user_data['today'] = today
        
        return JSONResponse(user_data)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))