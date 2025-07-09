# routes/auth.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json, os

router = APIRouter()

DATA_DIR = "database"
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure JSON files exist
for role in ["elder", "caregiver", "connections"]:
    path = os.path.join(DATA_DIR, f"{role}.json")
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

# Pydantic model
class User(BaseModel):
    username: str
    phone: str
    password: str

# Utility functions
def get_path(role): return os.path.join(DATA_DIR, f"{role}.json")

def load_data(role):
    with open(get_path(role), "r") as f:
        return json.load(f)

def save_data(role, data):
    with open(get_path(role), "w") as f:
        json.dump(data, f, indent=2)

@router.post("/auth/{action}/{role}")
def handle_user(action: str, role: str, user: User):
    if role not in ["elder", "caregiver"]:
        raise HTTPException(status_code=400, detail="Role must be 'elder' or 'caregiver'")
    if action not in ["signup", "login"]:
        raise HTTPException(status_code=400, detail="Action must be 'signup' or 'login'")

    data = load_data(role)

    if action == "signup":
        if user.username in data:
            raise HTTPException(status_code=400, detail="User already exists")
        data[user.username] = user.model_dump()
        save_data(role, data)

        return RedirectResponse(
            url=f"/askdata.html?username={user.username}&role={role}",
            status_code=303
        )

    elif action == "login":
        if user.username not in data:
            raise HTTPException(status_code=404, detail="User not found")
        if data[user.username]["password"] != user.password:
            raise HTTPException(status_code=401, detail="Incorrect password")
        return {"message": f"Login successful. Welcome {user.username}!"}
