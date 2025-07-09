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

# Single data file for all medicine tracking
DATABASE_DIR = "medicine_database"
DATA_FILE = "default_data.json"
DATABASE_PATH = Path(DATABASE_DIR) / DATA_FILE

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
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

def save_data(data: dict):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("/elder/medicine", response_class=HTMLResponse)
async def medicine_page(request: Request):
    data = load_data()
    
    # Add today's date to the context
    today = date.today().isoformat()
    
    return templates.TemplateResponse("elder_medicine.html", {
        "request": request,
        "initial_data": data,
        "today": today
    })

@router.post("/elder/save_medicine")
async def save_medicine(request: Request):
    try:
        incoming_data = await request.json()
        current_data = load_data()
        
        # Validate and update medicines list
        if 'medicines' in incoming_data:
            if not isinstance(incoming_data['medicines'], list):
                raise HTTPException(status_code=400, detail="Medicines must be a list")
            current_data['medicines'] = incoming_data['medicines']
        
        # Validate and update tracking data
        if 'tracking' in incoming_data:
            if not isinstance(incoming_data['tracking'], dict):
                raise HTTPException(status_code=400, detail="Tracking must be a dictionary")
            
            # Merge new tracking data with existing
            for key, value in incoming_data['tracking'].items():
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
        
            current_data['tracking'].update(incoming_data['tracking'])
        
        save_data(current_data)
        print("✅ Medicine data saved successfully")
        return JSONResponse({
            "status": "success", 
            "message": "Medicine data saved successfully"
        })
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/elder/load_medicine")
async def load_medicine():
    try:
        data = load_data()
        
        # Add today's date to the response
        today = date.today().isoformat()
        data['today'] = today
        
        return JSONResponse(data)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))