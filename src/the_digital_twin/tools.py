import os

import requests


def send_contact(email: str):
    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.environ["PUSHOVER_APP_TOKEN"],
            "user": os.environ["PUSHOVER_USER_KEY"],
            "title": "New Contact",
            "message": f"New contact email: {email}",
        }
    )

    response.raise_for_status()

    return {
        "success": True
    }

def store_out_of_context_ques(question: str):
    """
    Send an out-of-context question to the profile owner via Pushover.
    """

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.environ["PUSHOVER_APP_TOKEN"],
            "user": os.environ["PUSHOVER_USER_KEY"],
            "title": "AI Digital Twin - Out of Context Question",
            "message": f"User asked:\n{question}",
        },
        timeout=10,
    )

    response.raise_for_status()

    return {
        "success": True,
        "message": "Out-of-context question has been sent to the owner."
    }


tools = [
    {
        "type": "function",
        "name": "store_out_of_context_ques",
        "description": (
            "Send a user's question to the profile owner via Pushover "
            "when the question cannot be answered using the provided "
            "LinkedIn profile summary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The complete question asked by the user."
                }
            },
            "required": ["question"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "send_contact",
        "description": (
            "Send a user's email address to the profile owner via Pushover "
            "when the user wants to connect or contact the owner."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address provided by the user."
                }
            },
            "required": ["email"],
            "additionalProperties": False
        }
    }
]