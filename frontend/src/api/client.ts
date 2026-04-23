const base = import.meta.env.VITE_API_BASE ?? "/api";

function getToken(): string | null {
  return localStorage.getItem("req2veri_token");
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem("req2veri_token", token);
  else localStorage.removeItem("req2veri_token");
}

export async function apiFetch<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Accept", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  const res = await fetch(`${base}${path}`, { ...init, headers, body });
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail;
    const msg = typeof detail === "string" ? detail : JSON.stringify(detail ?? data);
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return data as T;
}
