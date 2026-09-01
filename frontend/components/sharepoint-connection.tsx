"use client";

import { useState } from "react";

import { apiFetch } from "@/lib/api/client";

type Item = { id: string; name: string; is_folder: boolean; is_video: boolean; web_url?: string };
type Connection = { site: { id: string; name?: string; web_url?: string }; drives: Array<{ id: string; name: string; items: Item[] }> };

export function SharePointConnection() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [children, setChildren] = useState<Record<string, Item[]>>({});
  const [videoUrl, setVideoUrl] = useState("");
  const [message, setMessage] = useState("");
  async function connect() {
    setMessage("Conectando con SharePoint…");
    try { const response = await apiFetch("/api/sharepoint/connection"); if (!response.ok) throw new Error((await response.json()).detail); setConnection(await response.json()); setMessage("Conexión establecida."); }
    catch (error) { setMessage(error instanceof Error ? error.message : "No se pudo conectar."); }
  }
  async function play(driveId: string, itemId: string) {
    try { const response = await apiFetch(`/api/sharepoint/drives/${driveId}/items/${itemId}/playback`, { method: "POST" }); if (!response.ok) throw new Error((await response.json()).detail); setVideoUrl((await response.json()).url); }
    catch (error) { setMessage(error instanceof Error ? error.message : "No se pudo abrir el video."); }
  }
  async function openFolder(driveId: string, itemId: string) {
    try { const response = await apiFetch(`/api/sharepoint/drives/${driveId}/items/${itemId}/children`); if (!response.ok) throw new Error((await response.json()).detail); const items = await response.json() as Item[]; setChildren((current) => ({ ...current, [itemId]: items })); }
    catch (error) { setMessage(error instanceof Error ? error.message : "No se pudo abrir la carpeta."); }
  }
  function renderItems(driveId: string, items: Item[], level = 0): React.ReactNode {
    return <ul className={level ? "mt-2 space-y-2 border-l border-slate-200 pl-4" : "mt-2 space-y-2"}>{items.map((item) => <li className="rounded border border-slate-200 px-3 py-2 text-sm" key={item.id}><div className="flex items-center justify-between gap-3"><span>{item.is_folder ? "Carpeta: " : "Archivo: "}{item.name}</span><span className="shrink-0">{item.is_folder && <button className="text-[#005a94] underline" onClick={() => void openFolder(driveId, item.id)}>Abrir</button>}{item.is_video && <button className="text-[#005a94] underline" onClick={() => void play(driveId, item.id)}>Reproducir</button>}</span></div>{children[item.id] && renderItems(driveId, children[item.id], level + 1)}</li>)}</ul>;
  }
  return <section className="app-card p-6"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm font-semibold text-[#004a7c]">Conexión real</p><h1 className="text-2xl font-bold">SharePoint</h1></div><button className="rounded bg-[#005a94] px-4 py-2 text-sm font-semibold text-white" onClick={() => void connect()}>Conectar y listar</button></div>{message && <p className="mt-4 text-sm text-slate-600">{message}</p>}{connection && <div className="mt-6 space-y-5"><p className="text-sm">Sitio: <a className="text-[#005a94] underline" href={connection.site.web_url} target="_blank">{connection.site.name ?? connection.site.id}</a></p>{connection.drives.map((drive) => <div key={drive.id}><h2 className="font-semibold">{drive.name}</h2>{renderItems(drive.id, drive.items)}</div>)}</div>}{videoUrl && <video className="mt-6 w-full rounded bg-black" controls src={videoUrl}>Tu navegador no puede reproducir este video.</video>}</section>;
}
