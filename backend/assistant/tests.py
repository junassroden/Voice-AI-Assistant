import json
from unittest.mock import patch

from django.test import SimpleTestCase


class AssistantApiTests(SimpleTestCase):
    def test_test_endpoint(self):
        response = self.client.get("/api/assistant/test/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Voice AI Assistant backend is working.")

    def test_chat_with_valid_message(self):
        response = self.client.post(
            "/api/assistant/chat/",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())

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

    @patch.dict("os.environ", {"ELEVENLABS_API_KEY": "", "ELEVENLABS_VOICE_ID": ""}, clear=False)
    def test_speak_without_credentials(self):
        response = self.client.post(
            "/api/assistant/speak/",
            data=json.dumps({"text": "Hello there"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 503)
