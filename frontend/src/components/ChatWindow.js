import React, { useEffect, useState, useRef } from "react";

const ChatWindow = (props) => {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [input, setInput] = useState("");
  const ws = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (props.sessionId !== null && props.sessionId !== undefined) {
      setSessionId(props.sessionId);
    }
  }, [props]);

  const fetchMessages = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/messages/chat/?session_id=${sessionId}`
      );
      const data = await response.json();
      setMessages(data.reverse());
      scrollToBottom();
    } catch (err) {
      console.error("Failed to fetch messages:", err);
    }
  };

  // scroll to the bottom when new messages appear
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    if (!sessionId) return;

    fetchMessages();

    const socketUrl = `ws://localhost:8000/ws/chat/${sessionId}/`;
    ws.current = new WebSocket(socketUrl);

    ws.current.onopen = () => {
      console.log("WebSocket Connected for session:", sessionId);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "chat_response") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
        scrollToBottom();
      }
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket Error:", error);
    };

    ws.current.onclose = () => {
      setSessionId(null);
      console.log("WebSocket Disconnected");
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [sessionId]);

  const sendMessage = () => {
    if (input.trim() !== "" && ws.current) {
      const message = {
        query: input,
        session_id: sessionId,
      };
      ws.current.send(JSON.stringify(message));
      setMessages((prev) => [...prev, { role: "user", content: input }]);
      setInput("");
      scrollToBottom();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div style={styles.container}>
        {!sessionId ? (

			<div style={styles.noSessionContainer}>
				<h3 style={styles.noSessionMsg}>Select or create a session.</h3>
			  </div>

        ) : (

			<>

		<div style={styles.header}>
          <span style={styles.sessionLabel}>Session ID: {sessionId}</span>
      	</div>

      <div style={styles.messages}>
        {messages.map((msg, idx) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={idx}
              style={{
                ...styles.messageRow,
                justifyContent: isUser ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  ...styles.messageBubble,
                  backgroundColor: isUser ? "#4f6ef7" : "#e3e9f3",
                  color: isUser ? "#fff" : "#000",
                }}
              >
                <div style={styles.messageAuthor}>
                  {isUser ? "You" : "AI"}
                </div>
                <div style={styles.messageContent}>{msg.content}</div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputContainer}>
        <input
          style={styles.input}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button style={styles.sendButton} onClick={sendMessage}>
          Send
        </button>
      </div>

			</>

        )}
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100%",
    backgroundColor: "#fff",
  },
  header: {
    padding: "10px 20px",
    backgroundColor: "#f0f2f5",
    borderBottom: "1px solid #ccc",
  },
  sessionLabel: {
    fontSize: "0.9rem",
    color: "#666",
  },
  noSessionMsg: {
    fontSize: "0.9rem",
    fontStyle: "italic",
    color: "#aaa",
  },
  messages: {
    flex: 1,
    padding: "10px 20px",
    overflowY: "auto",
  },
  messageRow: {
    display: "flex",
    marginBottom: 10,
  },
  messageBubble: {
    maxWidth: "60%",
    padding: "10px 15px",
    borderRadius: 12,
    lineHeight: 1.4,
    fontSize: "0.95rem",
  },
  messageAuthor: {
    fontSize: "0.7rem",
    marginBottom: 2,
    opacity: 0.8,
  },
  messageContent: {
    wordWrap: "break-word",
  },
  inputContainer: {
    display: "flex",
    borderTop: "1px solid #ccc",
    padding: 10,
    backgroundColor: "#f0f2f5",
  },
  input: {
    flex: 1,
    border: "1px solid #ccc",
    borderRadius: 4,
    padding: "8px 10px",
    outline: "none",
    fontSize: "1rem",
  },
  sendButton: {
    marginLeft: 10,
    padding: "8px 14px",
    backgroundColor: "#4f6ef7",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    borderRadius: 4,
    fontSize: "0.9rem",
  },

	noSessionContainer: {
		flex: 1,
		display: "flex",
		justifyContent: "center",
		alignItems: "center",
  },
  noSessionMsg: {
	  color: "#aaa",
  }
};

export default ChatWindow;

