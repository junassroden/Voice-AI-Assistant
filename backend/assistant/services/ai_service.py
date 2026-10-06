import os

import requests


def generate_ai_response(message: str) -> str:
    """Send a user message to the configured LLM and return the assistant text."""
    cleaned_message = (message or "").strip()
    if not cleaned_message:
        raise ValueError("Message cannot be empty.")

    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_response(cleaned_message)

    base_url = (os.getenv("LLM_API_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL") or "gpt-4o-mini"
    url = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": cleaned_message}],
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"LLM request failed: {exc}") from exc

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("LLM response format was invalid.") from exc

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("LLM returned an empty response.")

    return content.strip()


def _fallback_response(message: str) -> str:
    return (
        f"Thanks for your message: \"{message}\". "
        "I’m ready to help once the LLM API is configured."
    )
