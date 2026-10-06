function MessageBubble({ role, content }) {
  const isAssistant = role === "assistant";

  return (
    <div className={`message-row ${isAssistant ? "assistant" : "user"}`}>
      <div className={`message-bubble ${isAssistant ? "assistant" : "user"}`}>
        <div className="message-role">{isAssistant ? "ASSISTANT" : "USER"}</div>
        <p>{content}</p>
      </div>
    </div>
  );
}

export default MessageBubble;
