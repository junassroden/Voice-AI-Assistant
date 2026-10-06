function TextInput({ value, onChange, onSubmit, disabled }) {
  return (
    <form className="text-input-row" onSubmit={onSubmit}>
      <input
        type="text"
        value={value}
        onChange={onChange}
        disabled={disabled}
        placeholder="Ask something..."
        aria-label="Type a message"
      />
      <button type="submit" disabled={disabled}>
        Send
      </button>
    </form>
  );
}

export default TextInput;
