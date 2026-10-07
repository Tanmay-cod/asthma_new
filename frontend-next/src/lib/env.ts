/**
 * Public runtime configuration.
 * Only NEXT_PUBLIC_* variables are inlined into the browser bundle.
 * The service-role key, backend SECRET_KEY and ESP8266 device token
 * must never appear here.
 */

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

/** Versioned API prefix used by the FastAPI backend. */
export const API_PREFIX = "/api/v1";

export const SUPABASE_URL = (process.env.NEXT_PUBLIC_SUPABASE_URL || "").replace(
  /\/+$/,
  ""
);

export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export const POLL_INTERVAL_MS = 5000;
