"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getCourse } from "@/lib/api/catalog";
import { LessonThumbnail } from "@/components/lesson-thumbnail";

export default function CoursePage({ params }: { params: Promise<{ slug: string }> }) {
  const [course, setCourse] = useState<Awaited<ReturnType<typeof getCourse>> | null>(null);
  useEffect(() => { params.then(({ slug }) => getCourse(slug).then(setCourse)); }, [params]);

  return <main className="mx-auto max-w-5xl px-6 py-10"><section className="app-gradient rounded-2xl p-6 text-white"><p className="text-sm text-cyan-200">Curso</p><h1 className="mt-1 text-3xl font-bold">{course?.title ?? "Cargando…"}</h1><p className="mt-2 text-sm text-white/70">Completa cada video para desbloquear el siguiente.</p></section>{course?.modules.map((module) => <section className="mt-7" key={module.title}><h2 className="font-semibold text-slate-800">{module.title}</h2><div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{module.lessons.map((lesson, index) => {
    const document = lesson.type === "DOCUMENT";
    const action = document ? "Descargar archivo" : lesson.completed ? "Volver a ver" : lesson.progress_percent > 0 ? "Continuar viendo" : "Ver video";
    const card = <><div className="relative"><LessonThumbnail lessonId={lesson.id} locked={!lesson.unlocked} label={lesson.title} lessonType={lesson.type} /><span className={`absolute bottom-3 left-3 rounded px-2 py-1 text-xs font-semibold text-white ${document ? "bg-[#005a94]/85" : "bg-black/45"}`}>{document ? "Documento" : `Video ${index + 1}`}</span></div><div className="p-4"><h3 className="line-clamp-2 break-words text-sm font-semibold leading-5 text-slate-800">{lesson.title}</h3><p className="mt-2 text-xs text-slate-500">{document ? "Recurso complementario" : lesson.completed ? "✓ Visto" : lesson.unlocked && lesson.progress_percent > 0 ? "En progreso" : lesson.unlocked ? "Disponible" : "Completa el video anterior para desbloquearlo"}</p><span className={`mt-4 inline-flex rounded-full px-3 py-1 text-xs font-semibold ${lesson.completed ? "bg-emerald-100 text-emerald-800" : lesson.unlocked ? "bg-sky-100 text-sky-800" : "bg-slate-200 text-slate-500"}`}>{lesson.unlocked ? action : "Bloqueado"}</span></div></>;
    return lesson.unlocked ? <Link className="app-card app-card-hover overflow-hidden" href={`/lecciones/${lesson.id}`} key={lesson.id}>{card}</Link> : <div aria-disabled="true" className="app-card cursor-not-allowed overflow-hidden opacity-75" key={lesson.id}>{card}</div>;
  })}</div></section>)}</main>;
}
