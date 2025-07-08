from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "medicine_database"
os.makedirs(DATA_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def root():
    return FileResponse("static/medicine.html")

@app.get("/medicine/{user_id}")
def get_user_data(user_id: str):
    file_path = os.path.join(DATA_DIR, f"{user_id}_data.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

@app.post("/medicine/{user_id}")
async def update_user_data(user_id: str, request: Request):
    data = await request.json()
    file_path = os.path.join(DATA_DIR, f"{user_id}_data.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    return {"status": "saved"}
