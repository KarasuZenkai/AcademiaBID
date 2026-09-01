"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api/client";

export function LessonThumbnail({ lessonId, locked, label, lessonType }: { lessonId: string; locked: boolean; label: string; lessonType: string }) {
  const [url, setUrl] = useState("");

  useEffect(() => {
    if (lessonType !== "VIDEO") return;
    let objectUrl = "";
    apiFetch(`/api/lessons/${lessonId}/thumbnail`).then(async (response) => {
      if (!response.ok || response.status === 204) return;
      objectUrl = URL.createObjectURL(await response.blob());
      setUrl(objectUrl);
    }).catch(() => undefined);
    return () => { if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, [lessonId, lessonType]);

  const document = lessonType === "DOCUMENT";
  return <div className={`relative flex aspect-video items-center justify-center overflow-hidden ${locked ? "bg-slate-300" : document ? "bg-gradient-to-br from-slate-100 to-sky-100" : "bg-gradient-to-br from-[#003965] to-[#51b1db]"}`}>{url && <img alt={`Vista previa de ${label}`} className="absolute inset-0 h-full w-full object-cover" src={url} />}{document && !locked && <div className="relative z-10 flex flex-col items-center text-[#005a94]"><span className="text-4xl">📄</span><span className="mt-2 text-xs font-bold uppercase tracking-wider">Documento</span></div>}{!document && <span className={`relative z-10 grid h-11 w-11 place-items-center rounded-full text-lg ${locked ? "bg-slate-700/70 text-white" : "bg-black/45 text-white"}`}>{locked ? "🔒" : "▶"}</span>}{document && locked && <span className="relative z-10 grid h-11 w-11 place-items-center rounded-full bg-slate-700/70 text-lg text-white">🔒</span>}</div>;
}
