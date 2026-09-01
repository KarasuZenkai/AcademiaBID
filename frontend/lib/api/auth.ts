export type DevelopmentUser = {
  id: string;
  external_id: string;
  name: string;
  email: string;
  role: "ADMIN" | "LEARNER";
};

export type CurrentUser = DevelopmentUser & {
  groups: Array<{ id: string; name: string }>;
};

import { apiFetch, apiUrl } from "@/lib/api/client";

export async function getDevelopmentUsers(): Promise<DevelopmentUser[]> {
  const response = await fetch(`${apiUrl}/api/dev/users`);
  if (!response.ok) throw new Error("Could not load development users");
  return response.json() as Promise<DevelopmentUser[]>;
}

export async function getCurrentUser(externalId?: string): Promise<CurrentUser> {
  const response = await apiFetch("/api/me", { headers: externalId ? { "X-Dev-User-Id": externalId } : {} });
  if (!response.ok) throw new Error("Could not load current user");
  return response.json() as Promise<CurrentUser>;
}

export type ProfileDetails = { job_title: string | null; company_name: string | null };

export async function getProfileDetails(): Promise<ProfileDetails> {
  const response = await apiFetch("/api/me/profile");
  if (!response.ok) throw new Error("Could not load profile details");
  return response.json() as Promise<ProfileDetails>;
}
