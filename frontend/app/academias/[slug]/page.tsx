"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getAcademy, type LearningPath } from "@/lib/api/catalog";

export default function AcademyPage({ params }: { params: Promise<{ slug: string }> }) {
  const [paths, setPaths] = useState<LearningPath[]>([]); const [name, setName] = useState(""); const [error, setError] = useState("");
  useEffect(() => { params.then(({ slug }) => getAcademy(slug).then((academy) => { setName(academy.name); setPaths(academy.learning_paths); }).catch(() => setError("Academia no disponible."))); }, [params]);
  return <main className="mx-auto max-w-4xl px-6 py-10"><Link className="text-sm font-medium text-[#004a7c]" href="/academias">← Catálogo</Link><section className="app-gradient mt-5 rounded-2xl p-6 text-white"><p className="text-sm text-cyan-200">Academia</p><h1 className="mt-1 text-3xl font-bold">{name}</h1></section>{error && <p className="mt-4 text-red-700">{error}</p>}<div className="mt-6 grid gap-4 sm:grid-cols-2">{paths.map((path) => <Link className="app-card app-card-hover block p-5" href={`/rutas/${path.slug}`} key={path.slug}><span className="text-xs font-semibold uppercase tracking-wide text-[#005a94]">Ruta de aprendizaje</span><h2 className="mt-2 font-semibold text-slate-800">{path.name}</h2><p className="mt-3 text-sm text-slate-500">{path.course_count} curso{path.course_count === 1 ? "" : "s"} · {path.content_count} recurso{path.content_count === 1 ? "" : "s"}</p></Link>)}</div></main>;
}
