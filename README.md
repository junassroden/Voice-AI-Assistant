# Voice AI Assistant

A full-stack voice-enabled AI assistant built with React, Django REST Framework, Python, an LLM API, and ElevenLabs.

## Features

- Voice input via the browser Speech Recognition API
- Speech-to-text conversion
- AI conversational responses powered by an LLM
- Text-to-speech via ElevenLabs
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
LLM provider
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
- LLM API
- ElevenLabs API

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

Create `backend/.env` and add values like:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4o-mini
LLM_API_BASE_URL=https://api.openai.com/v1

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
- The app keeps the conversation in browser state for the initial implementation.
