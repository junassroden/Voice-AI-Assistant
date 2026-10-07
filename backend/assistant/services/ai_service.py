import os
from urllib.parse import urlsplit

import requests


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM provider is not configured."""


def generate_ai_response(
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    """Send a user message to the configured LLM and return the assistant text."""
    cleaned_message = (message or "").strip()
    if not cleaned_message:
        raise ValueError("Message cannot be empty.")

    base_url = (
        os.getenv("LLM_API_BASE_URL") or "https://api.groq.com/openai/v1"
    ).rstrip("/")
    provider_host = urlsplit(base_url).hostname or ""
    if provider_host == "api.groq.com" or provider_host.endswith(".groq.com"):
        api_key = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
    elif provider_host == "api.openai.com" or provider_host.endswith(".openai.com"):
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    else:
        api_key = (
            os.getenv("LLM_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

    if not api_key:
        raise LLMConfigurationError(
            "The AI is not configured. Add a Groq API key to backend/.env "
            "as GROQ_API_KEY or LLM_API_KEY."
        )

    model = os.getenv("LLM_MODEL") or "openai/gpt-oss-120b"
    url = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful voice assistant. Respond naturally and "
                    "concisely unless the user asks for more detail."
                ),
            },
            *(conversation_history or []),
            {"role": "user", "content": cleaned_message},
        ],
        "temperature": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise RuntimeError(
            "The AI provider timed out. Please try again."
        ) from exc
    except requests.ConnectionError as exc:
        raise RuntimeError(
            "Could not reach the AI provider. Check the backend internet "
            "connection and LLM_API_BASE_URL."
        ) from exc
    except requests.HTTPError as exc:
        response = exc.response
        status_code = response.status_code if response is not None else None
        if status_code == 401:
            message = (
                "The AI provider rejected the API key. Check the key in "
                "backend/.env."
            )
        elif status_code == 403:
            message = (
                "The AI provider denied access. Check your account and model "
                "permissions."
            )
        elif status_code == 404:
            message = (
                "The AI model or API endpoint was not found. Check "
                "LLM_MODEL and LLM_API_BASE_URL in backend/.env."
            )
        elif status_code == 429:
            message = (
                "The AI provider rate limit or usage quota was reached. Check "
                "your provider account and try again later."
            )
        elif status_code is not None and status_code >= 500:
            message = "The AI provider is temporarily unavailable. Please try again."
        else:
            status_detail = (
                f" (HTTP {status_code})" if status_code is not None else ""
            )
            message = (
                f"The AI provider rejected the request{status_detail}. Check "
                "the API key, model, and API URL in backend/.env."
            )
        raise RuntimeError(message) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "The AI provider request failed. Check the backend connection "
            "and provider settings."
        ) from exc

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError("LLM response format was invalid.") from exc

    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("LLM returned an empty response.")

    return content.strip()
