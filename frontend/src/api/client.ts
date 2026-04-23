const base = import.meta.env.VITE_API_BASE ?? "/api";

export class ApiError extends Error {
  status: number;
  path: string;
  detail: unknown;

  constructor(message: string, status: number, path: string, detail: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.path = path;
    this.detail = detail;
  }
}

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
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? (data as { detail: unknown }).detail
        : data;
    let msg =
      typeof detail === "string" && detail
        ? `${detail} (HTTP ${res.status})`
        : `HTTP ${res.status} on ${path}`;
    if (res.status === 401) {
      msg = `${msg}. Sign in again.`;
      setToken(null);
    }
    throw new ApiError(msg, res.status, path, detail);
  }
  return data as T;
}
