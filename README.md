# Voice AI Assistant

A full-stack voice-enabled AI assistant built with React, Django REST Framework, Python, Groq-hosted GPT-OSS, and optional ElevenLabs speech.

## Features

- Voice input via the browser Speech Recognition API
- Speech-to-text conversion
- AI conversational responses powered by the open-weight GPT-OSS model through Groq
- Text-to-speech via ElevenLabs, with browser speech as a fallback
- Conversation history in the client UI
- Typed message input support
- Responsive, portfolio-friendly interface
- Secure backend-only API integration for secrets

## Architecture

User
↓
React frontend
↓
Django REST API
↓
Groq-hosted GPT-OSS
↓
ElevenLabs TTS
↓
React frontend
↓
Audio playback

## Tech Stack

### Frontend
- React
- Vite
- JavaScript
- CSS

### Backend
- Python
- Django
- Django REST Framework
- django-cors-headers

### AI / Voice
- Groq API (OpenAI-compatible API for the GPT-OSS model)
- Optional ElevenLabs API (browser speech is used if it is unavailable)

## Local Setup

### 1. Backend

Open a PowerShell terminal and run:

```powershell
cd C:\Users\HP\Desktop\Projects\Voice-AI-Assistant\backend
.\venv\Scripts\activate
python manage.py runserver
```

### 2. Frontend

Open a second PowerShell terminal and run:

```powershell
cd C:\Users\HP\Desktop\Projects\Voice-AI-Assistant\frontend
npm install
npm run dev
```

The frontend will run at:
- http://localhost:5173

The backend will run at:
- http://127.0.0.1:8000

## Environment Variables

Create a free Groq API key, then set the Groq key, model, and API URL in `backend/.env` as shown below. The template is in `backend/.env.example`:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

GROQ_API_KEY=your_groq_api_key
LLM_MODEL=openai/gpt-oss-120b
LLM_API_BASE_URL=https://api.groq.com/openai/v1

ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

Do not commit `.env` or any real API keys to version control.

## API Endpoints

- `GET /api/assistant/test/`
- `POST /api/assistant/chat/`
- `POST /api/assistant/speak/`

## Notes

- Secret keys are stored only on the Django backend.
- The frontend communicates only with the Django API.
- Recent conversation turns are sent with each message so the model can respond in context.
- If ElevenLabs is not configured or unavailable, supported browsers speak the response locally.
- The AI endpoint requires a Groq API key. Without one, the backend returns a clear setup error rather than echoing the user's message.
