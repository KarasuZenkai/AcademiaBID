"use client";
import { useEffect, useState } from "react";
import { adminRequest } from "@/lib/api/admin";
import { getCurrentUser } from "@/lib/api/auth";

const presets = {
  academy: { path: "/api/admin/academies", method: "POST", body: { name: "Nueva academia", slug: "nueva-academia", description: "", is_published: false } },
  path: { path: "/api/admin/learning-paths", method: "POST", body: { academy_id: "UUID de academia", name: "Nueva ruta", slug: "nueva-ruta", position: 1, is_published: false } },
  course: { path: "/api/admin/courses", method: "POST", body: { title: "Nuevo curso", slug: "nuevo-curso", estimated_minutes: 30, is_published: false } },
  module: { path: "/api/admin/courses/UUID/modules", method: "POST", body: { course_id: "UUID", title: "Nuevo módulo", position: 1 } },
  lesson: { path: "/api/admin/modules/UUID/lessons", method: "POST", body: { module_id: "UUID", title: "Nueva lección", lesson_type: "VIDEO", position: 1, is_required: true, completion_threshold: 0.9, duration_seconds: 300, sharepoint_site_id: "", sharepoint_drive_id: "", sharepoint_item_id: "" } },
};

export function AdminConsole() {
  const [allowed, setAllowed] = useState<boolean | null>(null); const [overview, setOverview] = useState<Record<string, Array<Record<string, string | boolean>>> | null>(null);
  const [kind, setKind] = useState<keyof typeof presets>("academy"); const [path, setPath] = useState(presets.academy.path); const [method, setMethod] = useState(presets.academy.method); const [body, setBody] = useState(JSON.stringify(presets.academy.body, null, 2)); const [message, setMessage] = useState("");
  const reload = () => adminRequest<Record<string, Array<Record<string, string | boolean>>>>("/api/admin/overview").then(setOverview).catch((error) => setMessage(error.message));
  useEffect(() => { getCurrentUser(window.localStorage.getItem("academia-bid.development-user") ?? undefined).then((user) => { setAllowed(user.role === "ADMIN"); if (user.role === "ADMIN") reload(); }).catch(() => setAllowed(false)); }, []);
  function preset(next: keyof typeof presets) { const value=presets[next]; setKind(next); setPath(value.path); setMethod(value.method); setBody(JSON.stringify(value.body,null,2)); }
  async function submit(event: React.FormEvent) { event.preventDefault(); try { await adminRequest(path, method, body.trim() ? JSON.parse(body) : undefined); setMessage("Guardado. Actualiza UUIDs de los formularios hijos desde el resumen."); reload(); } catch (error) { setMessage(error instanceof Error ? error.message : "Error al guardar"); } }
  if (allowed === null) return <p>Cargando permisos…</p>; if (!allowed) return <p className="text-red-700">Solo un administrador puede acceder a este panel.</p>;
  return <div className="grid gap-8 lg:grid-cols-[1fr_1.2fr]"><section><h2 className="font-semibold">Contenido existente</h2>{overview && Object.entries(overview).map(([name, items]) => <details className="mt-3 rounded border p-3" key={name}><summary className="cursor-pointer">{name} ({items.length})</summary><pre className="mt-2 overflow-auto text-xs">{JSON.stringify(items, null, 2)}</pre></details>)}</section><form className="space-y-3" onSubmit={submit}><h2 className="font-semibold">Crear o editar contenido</h2><select className="w-full rounded border p-2" value={kind} onChange={(e) => preset(e.target.value as keyof typeof presets)}>{Object.keys(presets).map((item) => <option key={item}>{item}</option>)}</select><input className="w-full rounded border p-2" value={path} onChange={(e) => setPath(e.target.value)} /><select className="rounded border p-2" value={method} onChange={(e) => setMethod(e.target.value)}><option>POST</option><option>PATCH</option></select><textarea className="h-80 w-full rounded border p-3 font-mono text-xs" value={body} onChange={(e) => setBody(e.target.value)} /><button className="rounded bg-sky-700 px-4 py-2 text-white">Guardar</button>{message && <p className="text-sm">{message}</p>}</form></div>;
}
