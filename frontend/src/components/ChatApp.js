import React, { useEffect, useState } from "react";
import ChatWindow from "./ChatWindow";

const ChatApp = () => {
  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [newSessionName, setNewSessionName] = useState("New Session");

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/messages/session/")
      .then((response) => response.json())
      .then((data) => {
        setSessions(data);
      })
      .catch((error) => {
        console.error("Error fetching sessions:", error);
      });
  }, []);

  const handleNewSession = () => {
    const payload = { title: newSessionName };

    fetch("http://localhost:8000/api/v1/messages/session/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((newSession) => {
        setSessions((prev) => [...prev, newSession]);
        setSelectedSessionId(newSession.session_id);
      })
      .catch((error) => {
        console.error("Error creating new session:", error);
      });
  };

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
        <div style={styles.sidebarHeader}>
          <h2 style={styles.logo}>StoreChat 🗨️</h2>
          <div style={styles.newSessionContainer}>
            <input
              style={styles.newSessionInput}
              type="text"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              placeholder="Session name"
            />
            <button style={styles.newSessionBtn} onClick={handleNewSession}>
              + New
            </button>
          </div>
        </div>
        <div style={styles.sessionList}>
          {sessions.map((session) => (
            <div
              key={session.id}
              style={{
                ...styles.sessionItem,
                backgroundColor:
                  session.session_id === selectedSessionId ? "#e4ebf5" : "transparent",
                fontWeight:
                  session.session_id === selectedSessionId ? "600" : "400",
              }}
              onClick={() => setSelectedSessionId(session.session_id)}
            >
              <div style={styles.sessionTitle}>{session.title}</div>
              <small style={styles.sessionDate}>
                {new Date(session.created_at).toLocaleString()}
              </small>
            </div>
          ))}
        </div>
      </div>

      <div style={styles.chatArea}>
        <ChatWindow sessionId={selectedSessionId} />
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    height: "100vh",
    fontFamily: "Inter, sans-serif",
    color: "#333",
    backgroundColor: "#f7f9fc",
  },
  sidebar: {
    width: 300,
    borderRight: "1px solid #ccc",
    display: "flex",
    flexDirection: "column",
  },
  sidebarHeader: {
    padding: "20px",
    borderBottom: "1px solid #ccc",
  },
  logo: {
    margin: 0,
    marginBottom: 15,
    fontWeight: "600",
    fontSize: "1.4rem",
  },
  newSessionContainer: {
    display: "flex",
    gap: 5,
  },
  newSessionInput: {
    flex: 1,
    padding: 8,
    borderRadius: 4,
    border: "1px solid #ccc",
    outline: "none",
  },
  newSessionBtn: {
    padding: "8px 12px",
    backgroundColor: "#4f6ef7",
    border: "none",
    color: "#fff",
    cursor: "pointer",
    fontSize: "0.9rem",
    borderRadius: 4,
  },
  sessionList: {
    flex: 1,
    overflowY: "auto",
    padding: "10px 20px",
  },
  sessionItem: {
    padding: 12,
    marginBottom: 8,
    borderRadius: 4,
    cursor: "pointer",
    transition: "background-color 0.2s ease",
  },
  sessionTitle: {
    fontSize: "1rem",
    fontWeight: 500,
    marginBottom: 4,
  },
  sessionDate: {
    fontSize: "0.75rem",
    color: "#666",
  },
  chatArea: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
  },
};

export default ChatApp;

