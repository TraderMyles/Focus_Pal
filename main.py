from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import json, os
from utils import init_user_file

app = FastAPI()

DATA_DIR = "user_data"

class CheckIn(BaseModel):
    user_id: str
    duration_mins: int
    chapters_covered: list[str]  # ✅ Use list[str], not List[str]
    questions_done: int
    mock_done: bool
    notes: Optional[str] = None

@app.get("/")
def root():
    return {"message": "wassup world"}

@app.post("/register/{user_id}")
def register_user(user_id: str):
    filepath = f"{DATA_DIR}/{user_id}.json"

    if os.path.exists(filepath):
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = {
        "user_id": user_id,
        "streak_days": 0,
        "last_checkin": None,
        "check_ins": [],
        "milestones": {
            "total_hours": 0,
            "total_questions": 0,
            "chapters_completed": [],
            "mock_exams_done": 0,
            "total_sessions": 0
        }
    }

    with open(filepath, "w") as f:
        json.dump(user_data, f, indent=4)

    return {"message": f"User {user_id} registered successfully."}


@app.post("/checkin")
def checkin(data: CheckIn):
    filepath = f"{DATA_DIR}/{data.user_id}.json"
    init_user_file(data.user_id)

    # Load user file
    with open(filepath, "r") as f:
        user_data = json.load(f)

    today = datetime.today().strftime("%Y-%m-%d")
    last_checkin = user_data["last_checkin"]

    # --- Update streak ---
    if last_checkin:
        last_date = datetime.strptime(last_checkin, "%Y-%m-%d")
        if last_date == datetime.today() - timedelta(days=1):
            user_data["streak_days"] += 1
        elif last_date != datetime.today():
            user_data["streak_days"] = 1
    else:
        user_data["streak_days"] = 1

    user_data["last_checkin"] = today

    # --- Add check-in entry ---
    new_entry = {
        "date": today,
        "duration_mins": data.duration_mins,
        "chapters_covered": data.chapters_covered,
        "questions_done": data.questions_done,
        "mock_done": data.mock_done,
        "notes": data.notes
    }
    user_data["check_ins"].append(new_entry)

    # --- Update milestones ---
    milestones = user_data["milestones"]
    milestones["total_hours"] += round(data.duration_mins / 60, 2)
    milestones["total_questions"] += data.questions_done
    if data.mock_done:
        milestones["mock_exams_done"] += 1
    for chapter in data.chapters_covered:
        if chapter not in milestones["chapters_completed"]:
            milestones["chapters_completed"].append(chapter)

    # --- Save updated JSON ---
    with open(filepath, "w") as f:
        json.dump(user_data, f, indent=4)

    return {
        "message": "Check-in successful.",
        "streak_days": user_data["streak_days"],
        "milestones": milestones
    }

@app.get("/users")
def list_users():
    if not os.path.exists(DATA_DIR):
        raise HTTPException(status_code=500, detail="User data directory not found")

    user_files = os.listdir(DATA_DIR)
    user_ids = [filename.replace(".json", "") for filename in user_files if filename.endswith(".json")]

    return user_ids

@app.get("/summary/{user_id}")
def get_summary(user_id: str):
    filepath = f"{DATA_DIR}/{user_id}.json"

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="User not found")

    with open(filepath, "r") as f:
        user_data = json.load(f)

    return {
        "user_id": user_id,
        "streak_days": user_data["streak_days"],
        "last_checkin": user_data["last_checkin"],
        "milestones": {
            "total_hours": user_data["milestones"]["total_hours"],
            "total_questions": user_data["milestones"]["total_questions"],
            "mock_exams_done": user_data["milestones"]["mock_exams_done"],
            "chapters_completed": user_data["milestones"]["chapters_completed"],
            "total_sessions": user_data["milestones"]["total_sessions"],
        },
        "recent_check_ins": user_data["check_ins"][-3:][::-1]  # Last 3, newest first
    }
