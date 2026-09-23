from dotenv import load_dotenv
import os
import requests

load_dotenv()

def test_push(token: str, user: str) -> None:
    r = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": token,
            "user": user,
            "title": "Test",
            "message": "Pushover test from AI Digital Twin",
        },
        timeout=10,
    )
    print("status:", r.status_code)
    print("body:", r.text)

if __name__ == "__main__":
    token = os.getenv("PUSHOVER_APP_TOKEN")
    user = os.getenv("PUSHOVER_USER_KEY")
    print("token set:", bool(token), "user set:", bool(user))
    if not token or not user:
        print("MISSING KEYS")
    else:
        test_push(token, user)