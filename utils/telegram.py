import requests
import streamlit as st


def _bot_url(method: str) -> str:
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    return f"https://api.telegram.org/bot{token}/{method}"


def send_message(chat_id: str, text: str):
    """Sends a plain text message to a parent/student who has already
    messaged the bot at least once."""
    requests.post(_bot_url("sendMessage"), data={"chat_id": chat_id, "text": text})


def send_document(chat_id: str, file_path: str, caption: str = ""):
    """Sends a file (e.g. a fee receipt PDF) to a parent/student."""
    with open(file_path, "rb") as f:
        requests.post(
            _bot_url("sendDocument"),
            data={"chat_id": chat_id, "caption": caption},
            files={"document": f},
        )


def get_recent_registrations():
    """Fetches everyone who has messaged the bot recently, so the admin can
    match each Telegram user to a student/parent and save their chat_id.
    Returns a list of dicts: chat_id, name, username, text.
    """
    resp = requests.get(_bot_url("getUpdates"))
    data = resp.json()
    results = []
    seen_chat_ids = set()
    for update in data.get("result", []):
        message = update.get("message")
        if not message:
            continue
        chat = message.get("chat", {})
        chat_id = str(chat.get("id"))
        if chat_id in seen_chat_ids:
            continue
        seen_chat_ids.add(chat_id)
        results.append(
            {
                "chat_id": chat_id,
                "name": f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip(),
                "username": chat.get("username", ""),
                "text": message.get("text", ""),
            }
        )
    return results
