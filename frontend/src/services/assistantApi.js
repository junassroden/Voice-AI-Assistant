const API_BASE_URL = "http://127.0.0.1:8000/api/assistant";

async function request(url, options = {}, isAudio = false) {
  const response = await fetch(url, options);

  if (!response.ok) {
    let message = "Sorry, I couldn't connect to the assistant.";
    try {
      const errorData = await response.json();
      if (errorData && errorData.error) {
        message = errorData.error;
      }
    } catch {
      // Ignore invalid JSON and fall back to the default message.
    }
    throw new Error(message);
  }

  if (isAudio) {
    return response.blob();
  }

  return response.json();
}

export async function sendMessage(message) {
  return request(`${API_BASE_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });
}

export async function generateSpeech(text) {
  return request(
    `${API_BASE_URL}/speak/`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    },
    true,
  );
}
