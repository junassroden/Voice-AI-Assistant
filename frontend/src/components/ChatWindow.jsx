import MessageBubble from "./MessageBubble";

function ChatWindow({ messages }) {
  return (
    <section className="chat-window" aria-live="polite">
      {messages.length === 0 ? (
        <div className="empty-state">
          <p>Start a conversation by speaking or typing a question.</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <MessageBubble key={`${message.role}-${index}`} role={message.role} content={message.content} />
        ))
      )}
    </section>
  );
}

export default ChatWindow;
