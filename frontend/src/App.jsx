import { useRef, useState } from "react";

import ChatWindow from "./components/ChatWindow";
import Header from "./components/Header";
import StatusIndicator from "./components/StatusIndicator";
import TextInput from "./components/TextInput";
import VoiceButton from "./components/VoiceButton";
import { generateSpeech, sendMessage } from "./services/assistantApi";

const initialMessages = [];

function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [textInput, setTextInput] = useState("");
  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);

  const stopPlayback = () => {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  };

  const speakInBrowser = (text) => {
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      throw new Error("Voice playback is unavailable in this browser.");
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => setStatus("idle");
    utterance.onerror = () => {
      setErrorMessage("Voice playback is currently unavailable.");
      setStatus("error");
    };
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const appendMessage = (role, content) => {
    setMessages((current) => [...current, { role, content }]);
  };

  const handleSendMessage = async (trimmedText) => {
    if (!trimmedText) {
      return;
    }

    stopPlayback();
    setErrorMessage("");
    setStatus("processing");
    appendMessage("user", trimmedText);
    setTextInput("");

    try {
      const history = messages.map(({ role, content }) => ({ role, content }));
      const data = await sendMessage(trimmedText, history);
      const assistantText = data.response || "Sorry, I couldn't generate a response.";
      appendMessage("assistant", assistantText);
      setStatus("speaking");

      let browserFallbackStarted = false;
      const fallbackToBrowserSpeech = () => {
        if (browserFallbackStarted) {
          return;
        }
        browserFallbackStarted = true;
        try {
          speakInBrowser(assistantText);
        } catch {
          setErrorMessage("I answered in text, but voice playback is unavailable.");
          setStatus("idle");
        }
      };

      let audioUrl;
      try {
        const audioBlob = await generateSpeech(assistantText);
        audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          audioUrl = null;
          setStatus("idle");
        };

        audio.onerror = () => {
          if (audioUrl) {
            URL.revokeObjectURL(audioUrl);
            audioUrl = null;
          }
          fallbackToBrowserSpeech();
        };

        await audio.play();
      } catch {
        if (audioUrl) {
          URL.revokeObjectURL(audioUrl);
        }
        fallbackToBrowserSpeech();
      }
    } catch (error) {
      console.error(error);
      setErrorMessage(error.message || "Sorry, I couldn't generate a response.");
      setStatus("error");
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErrorMessage("Speech recognition is not supported in this browser.");
      setStatus("error");
      return;
    }

    if (status === "processing" || status === "speaking") {
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => {
      setErrorMessage("");
      setStatus("listening");
    };

    recognition.onresult = async (event) => {
      const transcript = event.results[0][0].transcript.trim();
      if (transcript) {
        await handleSendMessage(transcript);
      }
    };

    recognition.onerror = (event) => {
      if (event.error === "not-allowed" || event.error === "permission-denied") {
        setErrorMessage("Microphone access was denied.");
      } else {
        setErrorMessage("Sorry, I couldn't access the microphone.");
      }
      setStatus("error");
    };

    recognition.onend = () => {
      if (status !== "processing" && status !== "speaking") {
        setStatus("idle");
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmedText = textInput.trim();
    await handleSendMessage(trimmedText);
  };

  const handleClearConversation = () => {
    stopPlayback();
    setMessages(initialMessages);
    setTextInput("");
    setStatus("idle");
    setErrorMessage("");
  };

  return (
    <div className="app-shell">
      <Header />

      <div className="assistant-panel">
        <ChatWindow messages={messages} />

        <div className="controls-area">
          <StatusIndicator status={status} />

          <div className="controls-row">
            <VoiceButton
              status={status}
              onClick={startListening}
              disabled={status === "processing" || status === "speaking"}
            />

            <button type="button" className="secondary-button" onClick={handleClearConversation}>
              Clear conversation
            </button>
          </div>

          <TextInput
            value={textInput}
            onChange={(event) => setTextInput(event.target.value)}
            onSubmit={handleSubmit}
            disabled={status === "processing" || status === "speaking"}
          />
        </div>
      </div>

      {errorMessage && <p className="error-banner">{errorMessage}</p>}
    </div>
  );
}

export default App;