function VoiceButton({ status, onClick, disabled }) {
  const isListening = status === "listening";
  const isProcessing = status === "processing";
  const isSpeaking = status === "speaking";

  const label = isListening ? "Listening" : isProcessing ? "Thinking" : isSpeaking ? "Speaking" : "Start Speaking";

  return (
    <button
      type="button"
      className={`voice-button ${status}`}
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
    >
      <span className="mic-icon" aria-hidden="true">🎙️</span>
      <span>{label}</span>
    </button>
  );
}

export default VoiceButton;
