from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json, os
from fastapi.templating import Jinja2Templates

from fastapi import Request
from routes import caregiver_medicine,elder_medicine, profile, auth


app = FastAPI()

app.include_router(profile.router)
app.include_router(auth.router)
app.include_router(caregiver_medicine.router)
app.include_router(elder_medicine.router)
app.include_router(caregiver_medicine.router)

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

# Helpers
def get_path(role): return os.path.join(DATA_DIR, f"{role}.json")

def load_data(role):
    with open(get_path(role), "r") as f:
        return json.load(f)

def save_data(role, data):
    with open(get_path(role), "w") as f:
        json.dump(data, f, indent=2)

# root
print("Hello from your local code and the remote repo")

# Common login/signup handler
@app.post("/continue/{action}/{role}")
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

        # Redirect to askdata form with query parameters
        return RedirectResponse(
            url=f"/askdata.html?username={user.username}&role={role}",
            status_code=303
        )




    elif action == "login":
        if user.username not in data:
            raise HTTPException(status_code=404, detail="User not found")
        if data[user.username]["password"] != user.password:
            raise HTTPException(status_code=401, detail="Incorrect password")
        return {"message": f"Login successful. You are logged in as {data[user.username]['username']} ({role})"}

# Connection endpoint
@app.get("/connect")
def connect_users(elder_username: str, caregiver_username: str):
    elders = load_data("elder")
    caregivers = load_data("caregiver")
    if elder_username not in elders:
        raise HTTPException(status_code=404, detail="Elder not found")
    if caregiver_username not in caregivers:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    path = get_path("connections")
    connections = load_data("connections")
    connections[elder_username] = caregiver_username
    save_data("connections", connections)

    return {"message": f"Elder {elders[elder_username]['username']} connected with caregiver {caregivers[caregiver_username]['username']}"}

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")

