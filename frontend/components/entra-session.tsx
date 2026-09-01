"use client";

import { MsalProvider } from "@azure/msal-react";
import { useEffect, useState } from "react";

import { authorizationHeaders, entraEnabled, initializeEntra, msalInstance, signIn } from "@/lib/auth/entra";
import { apiUrl } from "@/lib/api/client";

export function EntraSession({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<"loading" | "anonymous" | "authenticated">(entraEnabled ? "loading" : "authenticated");
  useEffect(() => {
    if (!entraEnabled) return;
    void initializeEntra().then(() => {
      const account = msalInstance.getActiveAccount();
      setState(account ? "authenticated" : "anonymous");
      if (!account) return;
      const controller = new AbortController();
      const timeout = window.setTimeout(() => controller.abort(), 10_000);
      void authorizationHeaders().then((headers) => fetch(`${apiUrl}/api/sharepoint/sync`, { method: "POST", headers, signal: controller.signal })).catch(() => undefined).finally(() => window.clearTimeout(timeout));
    }).catch(() => setState("anonymous"));
  }, []);
  return <MsalProvider instance={msalInstance}>{state === "loading" ? <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/30"><p className="rounded bg-white px-4 py-3 text-sm">Preparando tu aprendizaje…</p></div> : state === "anonymous" ? <WelcomePage /> : children}</MsalProvider>;
}

function WelcomePage() {
  return <main className="min-h-screen overflow-hidden bg-[#f5f8fc] text-slate-900"><div className="mx-auto grid min-h-screen max-w-7xl items-center gap-8 px-6 py-12 lg:grid-cols-[1fr_1.1fr] lg:px-12"><section className="relative z-10"><p className="inline-flex rounded-full bg-[#005a94]/10 px-4 py-2 text-sm font-semibold text-[#005a94]">Academia BID</p><h1 className="mt-6 max-w-xl text-4xl font-extrabold tracking-tight text-[#002952] sm:text-6xl">Tu aprendizaje impulsa lo que sigue.</h1><p className="mt-5 max-w-lg text-lg leading-8 text-slate-600">Explora contenidos de tu unidad, avanza a tu ritmo y construye nuevas habilidades para llevarlas a la práctica.</p><button className="mt-8 rounded-xl bg-[#005a94] px-6 py-3 text-sm font-bold text-white shadow-lg shadow-[#005a94]/25 transition hover:bg-[#004a7c]" onClick={() => void signIn()}>Iniciar sesión con Microsoft</button><p className="mt-4 text-sm text-slate-500">Accede con tu cuenta corporativa de BID.</p></section><section className="relative"><div className="absolute inset-8 rounded-full bg-[#51b1db]/20 blur-3xl" /><img className="relative mx-auto w-full max-w-2xl drop-shadow-2xl" src="/academia-welcome-teacher.png" alt="Asistente de Academia BID con birrete y pizarrón" /></section></div></main>;
}
