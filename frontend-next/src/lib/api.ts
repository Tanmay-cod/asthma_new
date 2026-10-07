import { API_BASE_URL } from "./env";
import { getAccessToken } from "./authStore";

/** Typed client for the existing FastAPI backend (prefix /api/v1). */

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let token: string;
  try {
    token = await getAccessToken();
  } catch {
    throw new ApiError(401, "Not signed in");
  }

  const headers: Record<string, string> = {
    Authorization: `Bearer ${token}`,
    ...(init.headers as Record<string, string> | undefined),
  };
  if (init.body !== undefined && typeof init.body === "string") {
    headers["Content-Type"] = "application/json";
  }

  let res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });

  if (res.status === 401) {
    // Token may have expired between proactive refreshes: force one
    // refresh and retry exactly once.
    try {
      token = await getAccessToken(true);
    } catch {
      throw new ApiError(401, "Session expired; please sign in again");
    }
    res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { ...headers, Authorization: `Bearer ${token}` },
    });
  }

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    let message = `Request failed (${res.status})`;
    try {
      const parsed = JSON.parse(detail);
      if (parsed?.detail) message = parsed.detail;
    } catch {
      if (detail) message = detail;
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export const api = {
  get<T>(path: string): Promise<T> {
    return request<T>(path);
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  },
};

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Unexpected error";
}
