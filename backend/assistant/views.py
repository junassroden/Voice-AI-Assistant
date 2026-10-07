from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.ai_service import LLMConfigurationError, generate_ai_response
from .services.elevenlabs_service import generate_speech_audio


@api_view(["GET"])
def test_assistant(request):
    return Response({"message": "Voice AI Assistant backend is working."})


@api_view(["POST"])
def chat(request):
    payload = request.data or {}
    message = payload.get("message")

    if not isinstance(message, str) or not message.strip():
        return Response({"error": "Please provide a valid message."}, status=status.HTTP_400_BAD_REQUEST)

    history = payload.get("history", [])
    if not isinstance(history, list):
        return Response(
            {"error": "Conversation history must be a list."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    conversation_history = []
    for turn in history[-20:]:
        if (
            not isinstance(turn, dict)
            or turn.get("role") not in {"user", "assistant"}
            or not isinstance(turn.get("content"), str)
            or not turn["content"].strip()
        ):
            return Response(
                {"error": "Conversation history contains an invalid message."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        conversation_history.append(
            {"role": turn["role"], "content": turn["content"].strip()}
        )

    try:
        assistant_response = generate_ai_response(message, conversation_history)
    except LLMConfigurationError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except (RuntimeError, ValueError) as exc:
        return Response(
            {"error": str(exc) or "Sorry, I couldn't generate a response."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({"response": assistant_response})


@api_view(["POST"])
def speak(request):
    payload = request.data or {}
    text = payload.get("text")

    if not isinstance(text, str) or not text.strip():
        return Response({"error": "Please provide some text to speak."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        audio_data = generate_speech_audio(text)
    except (RuntimeError, ValueError):
        return Response(
            {"error": "Voice playback is currently unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return HttpResponse(audio_data, content_type="audio/mpeg", status=status.HTTP_200_OK)