let socket;

export const connectWebSocket = (sessionId, onMessage) => {
  socket = new WebSocket(`ws://localhost:8000/ws/chat/`);

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
	  console.log(data)
    onMessage(data);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected");
  };

  socket.onerror = (error) => {
    console.error("WebSocket Error:", error);
  };
};

export const sendMessage = (message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ message }));
  }
};

