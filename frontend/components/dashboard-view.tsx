"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getDashboard, type Dashboard } from "@/lib/api/dashboard";
import { useAchievements } from "@/components/achievements-overlay";
import { ProfileAvatar } from "@/components/profile-avatar";
import { getProfileDetails, type ProfileDetails } from "@/lib/api/auth";

export function DashboardView() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [profile, setProfile] = useState<ProfileDetails | null>(null);
  const [error, setError] = useState("");
  const { openAchievements } = useAchievements();

  useEffect(() => { getDashboard().then(setData).catch((item) => setError(item.message)); getProfileDetails().then(setProfile).catch(() => undefined); }, []);

  if (error) return <p className="text-red-700">{error}</p>;
  if (!data) return <p>Cargando tu aprendizaje…</p>;

  return <div className="space-y-7">
    <section className="app-gradient relative overflow-hidden rounded-2xl p-6 text-white">
      <div className="absolute inset-0 opacity-10 [background:radial-gradient(circle_at_80%_20%,#51b1db_0%,transparent_55%)]" />
      <div className="relative">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-center gap-4">
            <ProfileAvatar name={data.user_name} />
            <div>
            <p className="inline-flex rounded-full bg-white/10 px-3 py-1 text-xs text-cyan-200">Mi aprendizaje</p>
            <h1 className="mt-3 text-2xl font-bold">Hola, {data.user_name}</h1>
            {(profile?.job_title || profile?.company_name) && <p className="mt-1 text-sm text-cyan-100">{[profile.job_title, profile.company_name].filter(Boolean).join(" · ")}</p>}
            <p className="mt-1 text-sm text-white/70">Tu progreso general es {data.overall_progress_percent}%.</p>
            </div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/10 px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-cyan-100">Nivel {data.experience.level}</p>
            <p className="mt-1 text-xl font-bold">{data.experience.points} XP</p>
            <p className="mt-1 text-xs text-white/70">Faltan {data.experience.points_to_next_level} XP para el siguiente nivel</p>
          </div>
        </div>

        <div className="mt-7 border-t border-white/15 pt-5">
          <div className="flex items-baseline justify-between gap-3">
            <div><h2 className="font-semibold">Logros recientes</h2><p className="mt-1 text-xs text-white/65">Reconocimientos por cursos que has completado.</p></div>
            <span className="text-xs text-cyan-100">Últimos 5</span>
          </div>
          {data.badges.length ? <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">{data.badges.map((badge) => <button className="group rounded-xl border border-white/10 bg-[#00213f]/55 p-3 text-left transition hover:-translate-y-0.5 hover:bg-[#001a33]" onClick={openAchievements} key={badge.course_slug}>
            <span aria-hidden="true" className="flex h-11 w-11 items-center justify-center rounded-full border border-amber-200/40 bg-amber-300/15 text-xl shadow-inner shadow-amber-100/10">🏅</span>
            <span className="mt-3 block text-[10px] font-semibold uppercase tracking-wider text-cyan-200">Trofeo</span>
            <span className="mt-1 block text-sm font-semibold leading-snug text-white group-hover:text-cyan-100">Curso completado</span>
            <span className="mt-1 block text-xs leading-snug text-white/65">{badge.title}</span>
          </button>)}</div> : <button className="mt-4 rounded-xl border border-dashed border-white/20 bg-white/5 p-3 text-left text-sm text-white/70" onClick={openAchievements}>Completa tu primer curso para obtener una medalla.</button>}
        </div>
      </div>
    </section>

    <section>
      <h2 className="text-lg font-semibold text-slate-800">Continuar aprendiendo</h2>
      <div className="mt-3 grid gap-3">{data.continue_learning.length ? data.continue_learning.map((item) => <Link className="app-card app-card-hover p-4" href={`/lecciones/${item.lesson_id}`} key={item.lesson_id}>{item.lesson_title}<span className="mt-1 block text-sm text-slate-500">{item.course_title} · {item.progress_percent}% · continuar desde {item.resume_position_seconds}s</span></Link>) : <p className="app-card p-4 text-slate-500">Aún no tienes lecciones en progreso.</p>}</div>
    </section>

    <section>
      <h2 className="text-lg font-semibold text-slate-800">Cursos recientes</h2>
      <div className="mt-3 grid gap-4 sm:grid-cols-2">{data.recent_courses.map((course) => <Link className="app-card app-card-hover p-5" href={`/cursos/${course.slug}`} key={course.slug}><span className="font-semibold text-slate-800">{course.title}</span><div className="mt-3 h-1.5 rounded-full bg-slate-100"><div className="h-full rounded-full bg-[#51b1db]" style={{ width: `${course.progress_percent}%` }} /></div><span className="mt-2 block text-xs text-slate-500">{course.progress_percent}% completado</span></Link>)}</div>
    </section>
  </div>;
}
