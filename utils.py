import os
import json

def init_user_file(user_id: str):
    file_path = f"user_data/{user_id}.json"

    if not os.path.exists(file_path):
        user_template = {
            "user_id": user_id,
            "streak_days": 0,
            "last_checkin": None,
            "check_ins": [],
            "milestones": {
                "total_hours": 0,
                "total_questions": 0,
                "chapters_completed": [],
                "mock_exams_done": 0
            }
        }

        with open(file_path, "w") as f:
            json.dump(user_template, f, indent=4)
        print(f"Created blank file for user {user_id}")
    else:
        print(f"User file already exists for {user_id}")


