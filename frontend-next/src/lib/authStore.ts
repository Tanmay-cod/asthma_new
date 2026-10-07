import { refreshSession } from "./supabase";
import type { AuthSession } from "./types";

/**
 * Module-level auth session store (no React dependency).
 * The access token lives in memory + sessionStorage (tab-scoped, not
 * persisted across tabs/devices) and is never logged or rendered.
 */

const STORAGE_KEY = "asthma_dashboard_session";

let memory: AuthSession | null = null;

function storage(): Storage | null {
  return typeof window === "undefined" ? null : window.sessionStorage;
}

export function loadSession(): AuthSession | null {
  if (memory) return memory;
  const s = storage();
  if (!s) return null;
  try {
    const raw = s.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthSession;
    if (!parsed.accessToken || !parsed.refreshToken) return null;
    memory = parsed;
    return memory;
  } catch {
    return null;
  }
}

export function saveSession(session: AuthSession): void {
  memory = session;
  storage()?.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearSession(): void {
  memory = null;
  storage()?.removeItem(STORAGE_KEY);
}

let refreshing: Promise<AuthSession> | null = null;

function doRefresh(current: AuthSession): Promise<AuthSession> {
  if (!refreshing) {
    refreshing = refreshSession(current.refreshToken)
      .then((next) => {
        saveSession(next);
        return next;
      })
      .catch((err: unknown) => {
        clearSession();
        throw err;
      })
      .finally(() => {
        refreshing = null;
      });
  }
  return refreshing;
}

/**
 * Returns a usable access token, refreshing proactively when the token
 * is within 60s of expiry. Pass forceRefresh=true to retry after a 401.
 */
export async function getAccessToken(
  forceRefresh = false
): Promise<string> {
  let session = loadSession();
  if (!session) {
    throw new Error("not_authenticated");
  }
  const expired =
    session.expiresAt * 1000 - Date.now() < 60_000;
  if (forceRefresh || expired) {
    session = await doRefresh(session);
  }
  return session.accessToken;
}
