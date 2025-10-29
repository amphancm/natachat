import { fetchWithAuth } from "./api";

export type ChatRoom = {
  id: string;
  roomName: string;
  owner: string;
};

export type ChatHistoryMessage = {
  conversation_id: number;
  query: string;
  response: string;
  timestamp: string;
  senderUsername: string | null;
  rating: number | null;
};

const BASE = "/chat";

export async function createRoom(roomName: string): Promise<ChatRoom> {
  const res = await fetchWithAuth(`${BASE}/create-room?roomName=${encodeURIComponent(roomName)}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as ChatRoom;
}

export async function getRooms(): Promise<ChatRoom[]> {
  const res = await fetchWithAuth(`${BASE}/rooms`, { method: "GET" });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as ChatRoom[];
}

export async function getRoom(roomId: string): Promise<ChatRoom> {
  const res = await fetchWithAuth(`${BASE}/room/${roomId}`, { method: "GET" });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as ChatRoom;
}

export async function updateRoom(roomId: string, newName: string): Promise<ChatRoom> {
  const res = await fetchWithAuth(`${BASE}/room/${roomId}?new_name=${encodeURIComponent(newName)}`, {
    method: "PUT",
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as ChatRoom;
}

export async function deleteRoom(roomId: string): Promise<{ message: string }> {
  const res = await fetchWithAuth(`${BASE}/room/${roomId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as { message: string };
}

// 🆕 New API function to load message history
export async function getRoomHistory(roomId: string): Promise<ChatHistoryMessage[]> {
  const res = await fetchWithAuth(`${BASE}/history/${roomId}`, { method: "GET" });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.messages as ChatHistoryMessage[];
}

export default {
  createRoom,
  getRooms,
  getRoom,
  updateRoom,
  deleteRoom,
  getRoomHistory,
};
