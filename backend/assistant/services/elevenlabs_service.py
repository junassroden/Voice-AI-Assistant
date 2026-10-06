import os

import requests


def generate_speech_audio(text: str) -> bytes:
    """Generate and return MP3 audio bytes from the provided text."""
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise ValueError("Text cannot be empty.")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        raise RuntimeError("ElevenLabs API credentials are missing.")

    model_id = os.getenv("ELEVENLABS_MODEL_ID") or "eleven_multilingual_v2"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": cleaned_text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"ElevenLabs request failed: {exc}") from exc

    if not response.content:
        raise RuntimeError("ElevenLabs returned no audio data.")

    return response.content
