import { apiFetch } from "@/lib/api/client";

export async function adminRequest<T>(path: string, method = "GET", payload?: unknown): Promise<T> {
  const response = await apiFetch(path, { method, headers: { "Content-Type": "application/json" }, body: payload ? JSON.stringify(payload) : undefined });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed: ${response.status}`);
  return response.json() as Promise<T>;
}
