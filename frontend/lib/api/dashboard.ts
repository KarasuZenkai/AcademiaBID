import { apiFetch } from "@/lib/api/client";

export type Dashboard = { user_name: string; overall_progress_percent: number; experience: { points: number; level: number; points_to_next_level: number }; badges: Array<{ title: string; course_slug: string; awarded_at: string | null }>; continue_learning: Array<{ lesson_id: string; lesson_title: string; course_title: string; course_slug: string; resume_position_seconds: number; progress_percent: number }>; recent_courses: Array<{ title: string; slug: string; progress_percent: number }>; completed_courses: Array<{ title: string; slug: string }> };
export async function getDashboard(): Promise<Dashboard> { const response = await apiFetch("/api/dashboard"); if (!response.ok) throw new Error("No se pudo cargar el dashboard"); return response.json() as Promise<Dashboard>; }
export type Achievements = { experience: Dashboard["experience"]; badges: Array<{ title: string; awarded_at: string | null }> };
export async function getAchievements(): Promise<Achievements> { const response = await apiFetch("/api/logros"); if (!response.ok) throw new Error("No se pudieron cargar los logros"); return response.json() as Promise<Achievements>; }

export type ComplianceDashboard = {
  summary: { assigned_users: number; unit_count: number; completion_rate_percent: number; pending_assignments: number };
  units: Array<{ name: string; slug: string; assigned_users: number; course_count: number; completed_assignments: number; pending_assignments: number; average_progress_percent: number; completion_rate_percent: number }>;
  users: Array<{ name: string; units: string[]; average_progress_percent: number; completed_courses: number; pending_courses: number }>;
  attention_units: Array<{ name: string; completion_rate_percent: number; pending_assignments: number }>;
};
export async function getComplianceDashboard(): Promise<ComplianceDashboard> { const response = await apiFetch("/api/cumplimiento"); if (!response.ok) throw new Error("No tienes autorización para consultar el panel de cumplimiento."); return response.json() as Promise<ComplianceDashboard>; }
