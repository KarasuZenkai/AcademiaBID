"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { VideoPlayer } from "@/components/video-player";
import { getLesson } from "@/lib/api/catalog";
import { apiFetch } from "@/lib/api/client";

export default function LessonPage({ params }: { params: Promise<{ id: string }> }) {
  const [id, setId] = useState(""); const [lesson, setLesson] = useState<Awaited<ReturnType<typeof getLesson>> | null>(null); const [finished, setFinished] = useState(false);
  useEffect(() => { params.then(({ id: lessonId }) => { setId(lessonId); getLesson(lessonId).then(setLesson); }); }, [params]);
  const download = async () => {
    const response = await apiFetch(`/api/lessons/${id}/download`);
    if (!response.ok) return;
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url; link.download = lesson?.title ?? "documento"; link.click();
    URL.revokeObjectURL(url);
  };
  return <main className="mx-auto max-w-5xl px-6 py-10"><Link className="text-sm font-medium text-[#004a7c]" href="/academias">← Catálogo</Link><section className="app-card mt-5 p-6"><p className="text-sm font-semibold text-[#005a94]">Lección</p><h1 className="mt-1 line-clamp-2 break-all text-xl font-bold leading-7 text-slate-800 sm:text-2xl">{lesson?.title ?? "Cargando…"}</h1><p className="mt-2 text-slate-500">{lesson?.description}</p>{lesson?.lesson_type === "VIDEO" && id && <VideoPlayer lessonId={id} onEnded={() => setFinished(true)} />}{lesson?.lesson_type === "DOCUMENT" && <button className="mt-6 inline-flex rounded-lg bg-[#005a94] px-4 py-2 text-sm font-semibold text-white" onClick={() => void download()}>Descargar archivo</button>}{lesson?.lesson_type === "LINK" && lesson.external_url && <a href={lesson.external_url}>Abrir enlace</a>}{finished && lesson?.next_lesson && <div className="mt-6 overflow-hidden rounded-xl border border-[#005a94]/20 bg-sky-50"><div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center"><div className="flex h-20 w-full shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[#002952] to-[#51b1db] text-3xl text-white sm:w-36">▶</div><div><p className="text-xs font-semibold uppercase tracking-wide text-[#005a94]">A continuación</p><h2 className="mt-1 font-semibold text-slate-900">{lesson.next_lesson.title}</h2><p className="mt-1 text-sm text-slate-600">Terminaste este video. Continúa directamente con la siguiente lección.</p><Link className="mt-3 inline-flex rounded-lg bg-[#005a94] px-4 py-2 text-sm font-semibold text-white" href={`/lecciones/${lesson.next_lesson.id}`}>Ver siguiente video</Link></div></div></div>}</section></main>;
}
