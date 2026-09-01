import { authorizationHeaders } from "@/lib/auth/entra";

export const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, init: RequestInit = {}) {
  const headers = await authorizationHeaders();
  return fetch(`${apiUrl}${path}`, { ...init, headers: { ...headers, ...(init.headers ?? {}) } });
}
