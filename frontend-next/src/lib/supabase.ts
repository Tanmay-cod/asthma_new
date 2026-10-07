import { SUPABASE_ANON_KEY, SUPABASE_URL } from "./env";
import type { AuthSession } from "./types";

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  token_type: string;
  user: { id: string; email: string | null } | null;
}

function toSession(r: TokenResponse): AuthSession {
  return {
    accessToken: r.access_token,
    refreshToken: r.refresh_token,
    expiresAt: Math.floor(Date.now() / 1000) + (r.expires_in ?? 3600),
    userId: r.user?.id ?? "",
    email: r.user?.email ?? "",
  };
}

async function tokenRequest(
  grantType: string,
  body: Record<string, string>
): Promise<AuthSession> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
      "Supabase is not configured (NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY)"
    );
  }
  const res = await fetch(
    `${SUPABASE_URL}/auth/v1/token?grant_type=${grantType}`,
    {
      method: "POST",
      headers: {
        apikey: SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    }
  );
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    let message = "Sign-in failed";
    try {
      const parsed = JSON.parse(detail);
      if (parsed?.msg) message = parsed.msg;
      else if (parsed?.error) message = parsed.error;
    } catch {
      message = `Authentication failed (${res.status})`;
    }
    throw new Error(message);
  }
  return toSession((await res.json()) as TokenResponse);
}

/** Email + password sign-in against Supabase Auth (password grant). */
export function signInWithPassword(
  email: string,
  password: string
): Promise<AuthSession> {
  return tokenRequest("password", { email, password });
}

/** Refresh an expired access token using the stored refresh token. */
export function refreshSession(refreshToken: string): Promise<AuthSession> {
  return tokenRequest("refresh_token", { refresh_token: refreshToken });
}

/** Revoke the current session on the Supabase side. */
export async function signOut(accessToken: string): Promise<void> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) return;
  try {
    await fetch(`${SUPABASE_URL}/auth/v1/logout`, {
      method: "POST",
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
  } catch {
    // Best-effort: local session is cleared by the caller regardless.
  }
}
