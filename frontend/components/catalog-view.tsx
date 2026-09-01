"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getAcademies, type Academy } from "@/lib/api/catalog";
import { apiFetch } from "@/lib/api/client";

export function CatalogView() {
  const [academies, setAcademies] = useState<Academy[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const load = () => getAcademies().then((items) => { if (active) setAcademies(items); }).catch(() => { if (active) setError("No se pudo cargar el catálogo."); });
    void load();
    void apiFetch("/api/sharepoint/sync", { method: "POST" }).then((response) => response.ok ? load() : undefined).catch(() => undefined);
    return () => { active = false; };
  }, []);
  if (error) return <p className="text-red-700">{error}</p>;
  return <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{academies.map((academy) => <Link className="app-card app-card-hover p-5" href={`/academias/${academy.slug}`} key={academy.id}><div className="flex h-20 items-end rounded-lg bg-gradient-to-br from-[#003965] to-[#51b1db] p-3 text-white"><span className="text-sm font-semibold">Academia BID</span></div><h2 className="mt-4 font-semibold text-slate-800">{academy.name}</h2><p className="mt-2 text-sm text-slate-500">{academy.description}</p><p className="mt-4 text-xs font-medium text-[#005a94]">{academy.content_count} recurso{academy.content_count === 1 ? "" : "s"} · {academy.learning_path_count} ruta{academy.learning_path_count === 1 ? "" : "s"}</p></Link>)}</div>;
}
