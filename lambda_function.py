import json
import os
from datetime import datetime
from utils import init_user_file, build_prompt, generate_message, build_summary_string

def lambda_handler(event, context):
    user_id = event.get("user_id")

    if not user_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing user_id in event"})
        }

    try:
        init_user_file(user_id)
        prompt = build_prompt(user_id)
        message = generate_message(prompt, use_mock=True)  # Flip to True for testing
        summary = build_summary_string(user_id)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": message,
                "summary": summary,
                "date": datetime.today().strftime("%Y-%m-%d")
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
