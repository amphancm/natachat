import { jwtDecode } from "jwt-decode";
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export type TokenResponse = {
  access_token: string;
  token_type: string;
};


type DecodedToken = { sub?: string; exp?: number };

export function getUsernameFromToken(): string | null {
  try {
    const token = getToken();
    if (!token) return null;

    const decoded = jwtDecode<DecodedToken>(token);
    if (decoded && decoded.sub) return decoded.sub;

    return null;
  } catch (err) {
    console.error("JWT decode failed:", err);
    return null;
  }
}


export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });

  if (!res.ok) {
    let errMsg = res.statusText;
    try {
      const j = await res.json();
      errMsg = j.detail || j.error || JSON.stringify(j);
    } catch (e) {
      // ignore
    }
    throw new Error(errMsg || `HTTP ${res.status}`);
  }

  const data = await res.json();
  return data as TokenResponse;
}

export function getToken(): string | null {
  try {
    return localStorage.getItem("natachat_token");
  } catch (e) {
    return null;
  }
}

export function setToken(token: string) {
  try {
    localStorage.setItem("natachat_token", token);
  } catch (e) {
    // ignore
  }
}

export function clearToken() {
  try {
    localStorage.removeItem("natachat_token");
  } catch (e) {
    // ignore
  }
}

export async function fetchWithAuth(input: RequestInfo | string, init?: RequestInit) {
  const token = getToken();
  const headers = new Headers(init?.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const url = typeof input === "string" && input.startsWith("/") ? `${API_BASE}${input}` : (input as string);
  const res = await fetch(url, { ...init, headers });

  if (res.status === 401) {
    clearToken();
    throw new Error("Unauthorized");
  }

  return res;
}

export default {
  API_BASE,
  login,
  getToken,
  setToken,
  clearToken,
  fetchWithAuth,
  getUsernameFromToken
};
