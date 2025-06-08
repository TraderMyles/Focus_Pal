import os
import json
import openai
import boto3

def get_openai_key(secret_name="openapi", region_name="eu-west-2"):
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response["SecretString"])
        return secret_dict["openapi"]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch secret: {e}")

# Set the OpenAI API key
openai.api_key = get_openai_key()


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
                "mock_exams_done": 0,
                "total_sessions": 0
            }
        }

        with open(file_path, "w") as f:
            json.dump(user_template, f, indent=4)
        print(f"Created blank file for user {user_id}")
    else:
        print(f"User file already exists for {user_id}")


def build_prompt(user_id: str):
    filepath = f"user_data/{user_id}.json"

    if not os.path.exists(filepath):
        raise FileNotFoundError("User file not found.")

    with open(filepath, "r") as f:
        data = json.load(f)

    streak = data.get("streak_days", 0)
    last_checkin = data.get("check_ins", [])[-1] if data.get("check_ins") else None

    if not last_checkin:
        return "Write a motivational message for a student starting their study journey."

    minutes = last_checkin.get("duration_mins", 0)
    questions = last_checkin.get("questions_done", 0)

    return (
        f"Write a short motivational message for a student on a {streak}-day study streak "
        f"who studied {minutes} minutes yesterday and completed {questions} questions. "
        f"Make it positive, supportive, and no more than two sentences."
    )


def generate_message(prompt: str, use_mock=True):
    if use_mock:
        return f"[Mock AI Response] Based on prompt: {prompt}"
    
    # Real API call using older SDK
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # or "gpt-4" if available
        messages=[
            {"role": "system", "content": "You are a motivational coach for students."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=80
    )
    return response.choices[0]["message"]["content"].strip()


def build_summary_string(user_id: str):
    filepath = f"user_data/{user_id}.json"

    if not os.path.exists(filepath):
        return "[No summary available]"

    with open(filepath, "r") as f:
        data = json.load(f)

    streak = data.get("streak_days", 0)
    milestones = data.get("milestones", {})
    hours = milestones.get("total_hours", 0)
    questions = milestones.get("total_questions", 0)
    mocks = milestones.get("mock_exams_done", 0)
    sessions = milestones.get("total_sessions", len(data.get("check_ins", [])))

    return (
        f"📊 Daily Summary for {user_id}:\n"
        f"• Streak: {streak} days\n"
        f"• Total Hours: {hours}\n"
        f"• Total Questions: {questions}\n"
        f"• Mock Exams: {mocks}\n"
        f"• Total Sessions: {sessions}"
    )

def send_motivation_to_sns(message: str, summary: str, topic_arn: str):
    sns_client = boto3.client("sns", region_name="eu-west-2")
    
    full_message = f"{message}\n\n{summary}"  # 👈 Combine message + summary

    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=full_message,
        Subject="Your Daily Motivation 💪"
    )
    return response


if __name__ == "__main__":
    user_id = "MW001"

    prompt = build_prompt(user_id)
    print("📨 Prompt:\n", prompt)

    message = generate_message(prompt, use_mock=False)
    print("\n💬 Motivational Message:\n", message)

    summary = build_summary_string(user_id)
    print("\n📈 Summary:\n", summary)
