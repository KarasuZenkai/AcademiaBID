import { apiFetch } from "@/lib/api/client";

async function read<T>(path: string): Promise<T> {
  const response = await apiFetch(path);
  if (!response.ok) throw new Error(`Catalog request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export type Academy = { id: string; name: string; slug: string; description: string | null; learning_path_count: number; content_count: number; video_count: number };
export type LearningPath = { name: string; slug: string; description: string | null; position: number; course_count: number; content_count: number };
export type Course = { title: string; slug: string; description: string | null; estimated_minutes: number | null; position?: number; content_count: number; video_count: number };

export const getAcademies = () => read<Academy[]>("/api/academies");
export const getAcademy = (slug: string) => read<Academy & { learning_paths: LearningPath[] }>(`/api/academies/${slug}`);
export const getPath = (slug: string) => read<{ name: string; description: string | null; academy: Academy; courses: Course[] }>(`/api/rutas/${slug}`);
export const getCourse = (slug: string) => read<{ title: string; description: string | null; estimated_minutes: number | null; modules: Array<{ title: string; lessons: Array<{ id: string; title: string; type: string; progress_percent: number; resume_position_seconds: number; completed: boolean; unlocked: boolean }> }> }>(`/api/cursos/${slug}`);
export const getLesson = (id: string) => read<{ id: string; title: string; description: string | null; lesson_type: string; duration_seconds: number | null; external_url: string | null; next_lesson: { id: string; title: string } | null }>(`/api/lessons/${id}`);
export type Playback = { url: string; expires_at: string | null; duration_seconds: number | null; resume_position: number; session_id: string };
export type VideoProgress = { watched_seconds: number; progress_percent: number; last_position_seconds: number; completed: boolean; course_progress_percent: number };

export async function getPlayback(id: string): Promise<Playback> {
  const response = await apiFetch(`/api/lessons/${id}/playback`, { method: "POST" });
  if (!response.ok) throw new Error(`Playback request failed: ${response.status}`);
  return response.json() as Promise<Playback>;
}

export async function saveVideoProgress(id: string, payload: { position_seconds: number; duration_seconds: number; ranges: Array<{ start: number; end: number }>; session_id?: string }): Promise<VideoProgress> {
  const response = await apiFetch(`/api/lessons/${id}/progress`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), keepalive: true });
  if (!response.ok) throw new Error(`Progress request failed: ${response.status}`);
  return response.json() as Promise<VideoProgress>;
}
