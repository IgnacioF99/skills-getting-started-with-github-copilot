"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
from bson.objectid import ObjectId

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# MongoDB setup
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["mergington"]
activities_col = db["activities"]

# Actividades codificadas
PRELOADED_ACTIVITIES = {
    "Basketball Team": {
        "description": "Join the school basketball team and compete in local tournaments",
        "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Swimming Club": {
        "description": "Practice swimming techniques and participate in meets",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture with peers",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Team": {
        "description": "Develop argumentation skills and compete in debate tournaments",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": []
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

# Inicializar la base de datos si está vacía
def preload_activities():
    if activities_col.count_documents({}) == 0:
        for name, data in PRELOADED_ACTIVITIES.items():
            doc = {"_id": name, **data}
            activities_col.insert_one(doc)

preload_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    # Devuelve todas las actividades como dict
    acts = {}
    for doc in activities_col.find():
        d = dict(doc)
        d.pop("_id", None)
        acts[doc["_id"]] = d
    return acts


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    # Verificar si el estudiante ya está registrado en alguna actividad
    if activities_col.find_one({"participants": email}):
        raise HTTPException(status_code=400, detail="Student already signed up for an activity")
    # Validar que la actividad existe
    activity = activities_col.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activities_col.update_one({"_id": activity_name}, {"$push": {"participants": email}})
    return {"message": f"Signed up {email} for {activity_name}"}

# Endpoint para eliminar participante de una actividad
@app.delete("/activities/{activity_name}/signup")
def remove_participant(activity_name: str, email: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    activity = activities_col.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email not in activity["participants"]:
        raise HTTPException(status_code=404, detail="Participant not found in this activity")
    activities_col.update_one({"_id": activity_name}, {"$pull": {"participants": email}})
    return {"message": f"Removed {email} from {activity_name}"}
