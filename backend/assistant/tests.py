import json
import os
from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from .services.ai_service import LLMConfigurationError, generate_ai_response


class AssistantApiTests(SimpleTestCase):
    def test_test_endpoint(self):
        response = self.client.get("/api/assistant/test/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Voice AI Assistant backend is working.")

    @patch("assistant.views.generate_ai_response", return_value="Hello there.")
    def test_chat_with_valid_message(self, generate_response):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hello there."})
        generate_response.assert_called_once_with("Hello", [])

    @patch("assistant.views.generate_ai_response", return_value="It's sunny.")
    def test_chat_passes_conversation_history(self, generate_response):
        history = [
            {"role": "user", "content": "What's the weather?"},
            {"role": "assistant", "content": "Which city?"},
        ]
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": "Manila", "history": history}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        generate_response.assert_called_once_with("Manila", history)

    def test_chat_with_invalid_history(self):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps(
                {"message": "Hello", "history": [{"role": "system", "content": "x"}]}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_with_invalid_message(self):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_chat_with_missing_message(self):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    @patch(
        "assistant.views.generate_ai_response",
        side_effect=LLMConfigurationError("Missing key."),
    )
    def test_chat_reports_missing_provider_configuration(self, generate_response):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "Missing key.")
        generate_response.assert_called_once()

    @patch(
        "assistant.views.generate_ai_response",
        side_effect=RuntimeError("The AI provider rejected the API key."),
    )
    def test_chat_shows_actionable_provider_error(self, generate_response):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["error"], "The AI provider rejected the API key."
        )
        generate_response.assert_called_once()

    @patch.dict(
        "os.environ",
        {"ELEVENLABS_API_KEY": "", "ELEVENLABS_VOICE_ID": ""},
        clear=False,
    )
    def test_speak_without_credentials(self):
        response = self.client.post(
            "/api/assistant/speak/",
            data=json.dumps({"text": "Hello there"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)


class LLMServiceTests(SimpleTestCase):
    @patch.dict(
        os.environ,
        {
            "LLM_API_KEY": "",
            "GROQ_API_KEY": "",
            "OPENAI_API_KEY": "",
        },
        clear=False,
    )
    def test_missing_api_key_is_reported(self):
        with self.assertRaises(LLMConfigurationError):
            generate_ai_response("Hello")

    @patch.dict(
        os.environ,
        {
            "GROQ_API_KEY": "",
            "LLM_API_KEY": "",
            "OPENAI_API_KEY": "stale-openai-key",
            "LLM_API_BASE_URL": "https://api.groq.com/openai/v1",
        },
        clear=False,
    )
    def test_groq_does_not_use_an_openai_key(self):
        with self.assertRaises(LLMConfigurationError):
            generate_ai_response("Hello")

    @patch.dict(
        os.environ,
        {
            "LLM_API_KEY": "test-key",
            "GROQ_API_KEY": "",
            "LLM_API_BASE_URL": "https://api.groq.com/openai/v1",
            "LLM_MODEL": "openai/gpt-oss-120b",
        },
        clear=False,
    )
    @patch("assistant.services.ai_service.requests.post")
    def test_sends_authorized_request_with_conversation(self, post_request):
        post_request.return_value.json.return_value = {
            "choices": [{"message": {"content": "Hello back."}}]
        }
        history = [{"role": "user", "content": "Hi"}]

        result = generate_ai_response("How are you?", history)

        self.assertEqual(result, "Hello back.")
        post_request.assert_called_once()
        request = post_request.call_args
        self.assertEqual(
            request.kwargs["headers"]["Authorization"], "Bearer test-key"
        )
        self.assertEqual(
            request.args[0],
            "https://api.groq.com/openai/v1/chat/completions",
        )
        self.assertEqual(
            request.kwargs["json"]["model"], "openai/gpt-oss-120b"
        )
        self.assertEqual(
            request.kwargs["json"]["messages"][-2:],
            history + [{"role": "user", "content": "How are you?"}],
        )

    @patch.dict(
        os.environ,
        {
            "GROQ_API_KEY": "groq-test-key",
            "LLM_API_KEY": "stale-key",
            "OPENAI_API_KEY": "stale-openai-key",
            "LLM_API_BASE_URL": "https://api.groq.com/openai/v1",
            "LLM_MODEL": "openai/gpt-oss-120b",
        },
        clear=False,
    )
    @patch("assistant.services.ai_service.requests.post")
    def test_groq_api_key_takes_precedence(self, post_request):
        post_request.return_value.json.return_value = {
            "choices": [{"message": {"content": "Hello back."}}]
        }

        result = generate_ai_response("Hello")

        self.assertEqual(result, "Hello back.")
        self.assertEqual(
            post_request.call_args.kwargs["headers"]["Authorization"],
            "Bearer groq-test-key",
        )

    @patch("assistant.services.ai_service.requests.post")
    @patch.dict(os.environ, {"LLM_API_KEY": "test-key"}, clear=False)
    def test_invalid_provider_key_has_actionable_error(self, post_request):
        response = post_request.return_value
        response.status_code = 401
        post_request.side_effect = requests.HTTPError(response=response)

        with self.assertRaisesRegex(
            RuntimeError, "rejected the API key"
        ):
            generate_ai_response("Hello")
