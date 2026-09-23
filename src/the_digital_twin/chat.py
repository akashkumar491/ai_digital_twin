import json
import os

from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI

from .prompt import PROMPT
from .tools import send_contact, store_out_of_context_ques, tools

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "poolside/laguna-s-2.1"
PLACEHOLDER_API_KEY = "sk-or-placeholder"


def _get_openrouter_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY", PLACEHOLDER_API_KEY)
    except Exception:
        return os.getenv("OPENROUTER_API_KEY", PLACEHOLDER_API_KEY)


def _sync_pushover_secrets() -> None:
    """Push st.secrets into os.environ so tools.py sees them."""
    try:
        import streamlit as st
        for k in ("PUSHOVER_APP_TOKEN", "PUSHOVER_USER_KEY"):
            v = st.secrets.get(k)
            if v:
                os.environ[k] = v
    except Exception:
        pass


def get_client() -> OpenAI:
    _sync_pushover_secrets()
    return OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=_get_openrouter_key(),
        default_headers={
            "HTTP-Referer": "http://localhost:7860",
            "X-Title": "AI Digital Twin",
        },
    )


def run_tool(name: str, arguments: dict) -> str:
    func = {"store_out_of_context_ques": store_out_of_context_ques, "send_contact": send_contact}.get(name)
    if func is None:
        return f"Unknown tool: {name}"
    try:
        return str(func(**arguments))
    except Exception as exc:
        return f"Tool '{name}' failed: {exc}"


def handle_tool_calls(message) -> list[dict]:
    results = []
    for tool_call in message.tool_calls:
        arguments = json.loads(tool_call.function.arguments or "{}")
        results.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": run_tool(tool_call.function.name, arguments),
            }
        )
    return results


OUT_OF_SCOPE_SIGNALS = [
    "don't have information",
    "not available in my profile",
    "outside my profile",
    "can't answer",
    "cannot answer",
    "no information",
    "unavailable in the profile",
]


def chat(message: str, history: list) -> str:
    history = history or []
    messages = (
        [{"role": "system", "content": PROMPT}]
        + history
        + [{"role": "user", "content": message}]
    )

    tool_called_this_turn = False
    client = get_client()

    try:
        while True:
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t.get("description", ""),
                            "parameters": t.get("parameters", {}),
                        },
                    }
                    for t in tools
                ],
                tool_choice="auto",
                max_tokens=600,
            )
            assistant_message = response.choices[0].message

            if assistant_message.tool_calls:
                tool_called_this_turn = True
                messages.append(assistant_message.model_dump(exclude_none=True))
                messages.extend(handle_tool_calls(assistant_message))
                continue

            content = assistant_message.content or ""

            if not tool_called_this_turn and any(signal in content.lower() for signal in OUT_OF_SCOPE_SIGNALS):
                fallback_result = run_tool("store_out_of_context_ques", {"question": message})
                content = f"{content}\n\n[Auto-notification sent: {fallback_result}]"

            return content

    except AuthenticationError:
        return (
            "API key missing or invalid. Set OPENROUTER_API_KEY in .env "
            "or Streamlit secrets."
        )
    except Exception as exc:
        return f"Request failed: {exc}"