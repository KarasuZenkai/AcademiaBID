import { apiFetch } from "@/lib/api/client";

export async function adminRequest<T>(path: string, method = "GET", payload?: unknown): Promise<T> {
  const response = await apiFetch(path, { method, headers: { "Content-Type": "application/json" }, body: payload ? JSON.stringify(payload) : undefined });
  if (!response.ok) throw new Error((await response.json().catch(() => null))?.detail ?? `Request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export type AdminOverview = {
  users: Array<{ id: string; name: string; email: string; role: string; active: boolean }>;
  academies: Array<{ id: string; name: string; slug: string; published: boolean }>;
  paths: Array<{ id: string; name: string; academy_id: string }>;
  courses: Array<{ id: string; title: string; slug: string; published: boolean }>;
  modules: Array<{ id: string; title: string; course_id: string }>;
};

export type LearningAssignment = { user_id: string; user_name: string; target_type: "ACADEMY" | "LEARNING_PATH" | "COURSE" | "MODULE"; target_id: string; target_name: string; target_label: string; assigned_at: string };
export type CoursePrerequisite = { course_id: string; course_title: string; prerequisite_course_id: string; prerequisite_course_title: string };
