"use client";
import { DevelopmentUserSelector } from "@/components/development-user-selector";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAchievements } from "@/components/achievements-overlay";
import { getCurrentUser } from "@/lib/api/auth";
import { useEffect, useState } from "react";

const isLocalAuth = (process.env.NEXT_PUBLIC_AUTH_PROVIDER ?? "local") === "local";

export function AppHeader() {
  const pathname = usePathname();
  const { openAchievements } = useAchievements();
  const [isAdmin, setIsAdmin] = useState(false);
  useEffect(() => { getCurrentUser().then((user) => setIsAdmin(user.role === "ADMIN")).catch(() => undefined); }, []);
  const navigation = [["/mi-aprendizaje", "Mi aprendizaje"], ["/academias", "Academias"], ["/bid-it", "Bid It!"]];
  return (
    <>
      <header className="fixed inset-x-0 top-0 z-20 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4 md:hidden"><Link className="font-bold text-[#004a7c]" href="/mi-aprendizaje">Academia BID</Link>{isLocalAuth && <DevelopmentUserSelector />}</header>
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col bg-gradient-to-b from-[#002952] to-[#001429] md:flex">
        <div className="border-b border-white/10 px-5 py-5"><p className="text-sm font-bold text-white">Academia BID</p><p className="mt-1 text-xs text-white/50">Centro de aprendizaje</p></div>
        <nav className="flex-1 px-3 py-5"><p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-white/30">Principal</p><ul className="space-y-1">{navigation.map(([href, label]) => <li key={href}><Link className={`sidebar-item flex rounded-lg px-3 py-2.5 text-sm font-medium text-white/70 hover:text-white ${pathname === href ? "sidebar-item-active text-white" : ""}`} href={href}>{label}</Link></li>)}<li><button className="sidebar-item flex w-full rounded-lg px-3 py-2.5 text-left text-sm font-medium text-white/70 hover:text-white" onClick={openAchievements}>Logros</button></li>{isAdmin && <><li><Link className={`sidebar-item flex rounded-lg px-3 py-2.5 text-sm font-medium text-white/70 hover:text-white ${pathname === "/cumplimiento" ? "sidebar-item-active text-white" : ""}`} href="/cumplimiento">Cumplimiento</Link></li><li><Link className={`sidebar-item flex rounded-lg px-3 py-2.5 text-sm font-medium text-white/70 hover:text-white ${pathname === "/admin" ? "sidebar-item-active text-white" : ""}`} href="/admin">Administración</Link></li></>}</ul></nav>
        <div className="border-t border-white/10 px-4 py-4"><p className="mb-2 text-xs text-white/40">Usuario actual</p>{isLocalAuth ? <DevelopmentUserSelector dark compact /> : <p className="text-xs text-white/70">Sesión Microsoft Entra</p>}<p className="mt-4 text-xs text-white/30">Academia BID · Local</p></div>
      </aside>
    </>
  );
}
