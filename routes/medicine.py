from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os, json

router = APIRouter()
DATA_DIR = "database"

def get_path(role): 
    return os.path.join(DATA_DIR, f"{role}.json")

def load_data(role):
    with open(get_path(role), "r") as f:
        return json.load(f)

def save_data(role, data):
    with open(get_path(role), "w") as f:
        json.dump(data, f, indent=2)

@router.get("/elder/{username}/load_medicine")
async def load_medicine(username: str):
    elders = load_data("elder")
    if username not in elders:
        raise HTTPException(status_code=404, detail="User not found")

    medicines = elders[username].get("medicines", [])
    tracking = elders[username].get("tracking", {})

    return {"medicines": medicines, "tracking": tracking}

@router.post("/elder/{username}/save_medicine")
async def save_medicine(username: str, request: Request):
    elders = load_data("elder")
    if username not in elders:
        raise HTTPException(status_code=404, detail="User not found")

    body = await request.json()
    medicines = body.get("medicines")
    tracking = body.get("tracking")

    if medicines is None or tracking is None:
        raise HTTPException(status_code=400, detail="Missing medicines or tracking data")

    elders[username]["medicines"] = medicines
    elders[username]["tracking"] = tracking
    save_data("elder", elders)

    return JSONResponse(content={"message": "Medicine data saved successfully"})
