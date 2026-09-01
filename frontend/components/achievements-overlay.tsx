"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { getAchievements, type Achievements } from "@/lib/api/dashboard";

type AchievementsContextValue = { openAchievements: () => void };
const AchievementsContext = createContext<AchievementsContextValue | null>(null);

export function AchievementsProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<Achievements | null>(null);

  useEffect(() => { if (open) getAchievements().then(setData); }, [open]);

  return <AchievementsContext.Provider value={{ openAchievements: () => setOpen(true) }}>{children}{open && <div aria-modal="true" className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4" role="dialog"><section className="max-h-[85vh] w-full max-w-4xl overflow-y-auto rounded-2xl bg-white p-6 shadow-2xl"><div className="flex items-start justify-between gap-4"><div><p className="text-sm font-semibold text-[#005a94]">Academia BID</p><h2 className="mt-1 text-2xl font-bold text-slate-800">Mis logros</h2><p className="mt-2 text-sm text-slate-500">{data ? `${data.experience.points} XP · Nivel ${data.experience.level}` : "Cargando logros…"}</p></div><button aria-label="Cerrar logros" className="rounded-lg px-3 py-2 text-slate-500 hover:bg-slate-100" onClick={() => setOpen(false)}>✕</button></div>{data?.badges.length ? <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{data.badges.map((badge, index) => <article className="rounded-xl border border-slate-200 bg-slate-50 p-4" key={`${badge.title}-${index}`}><span aria-hidden="true" className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-2xl">🏅</span><p className="mt-4 text-xs font-semibold uppercase tracking-wide text-[#005a94]">Trofeo</p><h3 className="mt-1 font-semibold text-slate-800">Curso completado</h3><p className="mt-1 text-sm text-slate-500">{badge.title}</p></article>)}</div> : data && <p className="mt-6 rounded-xl bg-slate-50 p-5 text-slate-500">Aún no tienes medallas. Completa un curso para obtener la primera.</p>}</section></div>}</AchievementsContext.Provider>;
}

export function useAchievements() {
  const context = useContext(AchievementsContext);
  if (!context) throw new Error("useAchievements must be used inside AchievementsProvider");
  return context;
}
