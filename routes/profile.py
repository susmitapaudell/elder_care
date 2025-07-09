# routes/profile.py

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
import json, os

router = APIRouter()

DATA_DIR = "database"

def get_path(role): return os.path.join(DATA_DIR, f"{role}.json")

def load_data(role):
    with open(get_path(role), "r") as f:
        return json.load(f)

def save_data(role, data):
    with open(get_path(role), "w") as f:
        json.dump(data, f, indent=2)


@router.post("/profile/{role}/{username}")
def save_profile(role: str, username: str,
                 full_name: str = Form(...),
                 dob: str = Form(...),
                 blood_group: str = Form(...),
                 height_cm: float = Form(...),
                 weight_kg: float = Form(...)):
    
    if role not in ["elder", "caregiver"]:
        return {"error": "Invalid role"}

    data = load_data(role)

    if username not in data:
        return {"error": "User not found"}

    # Add extra profile data
    data[username].update({
        "full_name": full_name,
        "dob": dob,
        "blood_group": blood_group,
        "height_cm": height_cm,
        "weight_kg": weight_kg
    })

    save_data(role, data)

    # ✅ Redirect to home.html
    return RedirectResponse(url="/home.html", status_code=303)
