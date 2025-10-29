import { getUsernameFromToken } from "./api";

const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace(/^http/, "ws") || "ws://localhost:8000";

export function connectChatSocket(
  roomId: string,
  onMessage: (msg: string) => void,
  onError?: (err: string) => void,
) {
  const username = getUsernameFromToken() || "guest";
  const socket = new WebSocket(`${API_BASE}/ws/chat/${roomId}/${username}`);

  socket.onopen = () => {
    // ready to send/receive
  };

  socket.onmessage = (event) => onMessage(event.data);
  socket.onerror = () => onError?.("WebSocket connection error");
  socket.onclose = () => onError?.("WebSocket closed unexpectedly");

  return socket;
}
