"use client";

import { useEffect, useState } from "react";

import { getHealth, type HealthStatus } from "@/lib/api/health";

export function HealthStatusCard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setError("No se pudo conectar con el backend."));
  }, []);

  if (error) return <p className="text-red-700">{error}</p>;
  if (!health) return <p className="text-slate-600">Comprobando API…</p>;

  return (
    <p className="text-emerald-700">
      API: {health.status} · PostgreSQL: {health.database}
    </p>
  );
}
