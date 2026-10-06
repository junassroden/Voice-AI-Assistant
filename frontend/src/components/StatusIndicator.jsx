function StatusIndicator({ status }) {
  const labels = {
    idle: "Click the microphone to speak.",
    listening: "Listening...",
    processing: "Thinking...",
    speaking: "Speaking...",
    error: "Something went wrong.",
  };

  return <div className="status-indicator">{labels[status] || labels.idle}</div>;
}

export default StatusIndicator;
