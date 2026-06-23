import requests
from django.conf import settings


class N8nChatError(Exception):
    """Raised when the n8n chat webhook fails or returns an invalid payload."""


ENGLISH_ONLY_INSTRUCTION = (
    "Always respond in English only. Do not use Bengali, Hindi, Arabic, "
    "or any language other than English."
)


def send_n8n_message(message, session_id, trip_context):
    if not settings.N8N_CHAT_WEBHOOK_URL:
        raise N8nChatError(
            "The travel assistant is not configured. Please try again later."
        )

    payload = {
        "action": "sendMessage",
        "sessionId": session_id,
        "chatInput": (
            f"{ENGLISH_ONLY_INSTRUCTION}\n\n"
            f"User question: {message}"
        ),
        "rawUserMessage": message,
        "language": "en",
        "locale": "en-US",
        "respondInEnglish": True,
        "systemMessage": ENGLISH_ONLY_INSTRUCTION,
        "systemPrompt": ENGLISH_ONLY_INSTRUCTION,
        "search_id": trip_context.get("search_id"),
        "from_city": trip_context.get("city_departure_code"),
        "to_city": trip_context.get("city_arrival_code"),
        "flight_date": trip_context.get("selected_departure_date"),
        "stay_days": trip_context.get("stay_days"),
        "timespan_to_search": trip_context.get("search_window_days"),
        "price_usd": trip_context.get("selected_price_usd"),
        "metadata": {
            **trip_context,
            "language": "en",
            "locale": "en-US",
            "respond_in_english": True,
            "assistant_instruction": ENGLISH_ONLY_INSTRUCTION,
        },
    }

    try:
        response = requests.post(
            settings.N8N_CHAT_WEBHOOK_URL,
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise N8nChatError(
            "Could not reach the travel assistant. Please try again in a moment."
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise N8nChatError("The assistant returned an invalid response.") from exc

    if isinstance(data, str):
        return data

    for key in ("output", "text", "message", "reply"):
        if data.get(key):
            return data[key]

    raise N8nChatError("The assistant returned an empty response.")
