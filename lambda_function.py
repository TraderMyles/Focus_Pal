import json
import os
from datetime import datetime
from utils import init_user_file, build_prompt, generate_message, build_summary_string, send_motivation_to_sns

SNS_TOPIC_ARN = "arn:aws:sns:eu-west-2:962804303545:study-helper"

def lambda_handler(event, context):
    user_id = event.get("user_id", "MW001")

    if not user_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing user_id in event"})
        }

    try:
        init_user_file(user_id)
        prompt = build_prompt(user_id)
        message = generate_message(prompt, use_mock=True)  # Set to False when ready
        summary = build_summary_string(user_id)

        # 🔔 Send motivation via SNS
        sns_response = send_motivation_to_sns(message, summary, SNS_TOPIC_ARN)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": message,
                "summary": summary,
                "date": datetime.today().strftime("%Y-%m-%d"),
                "snsMessageId": sns_response.get("MessageId")
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }