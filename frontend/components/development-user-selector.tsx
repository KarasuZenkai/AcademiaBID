"use client";

import { useEffect, useState } from "react";

import { getCurrentUser, getDevelopmentUsers, type DevelopmentUser } from "@/lib/api/auth";

const storageKey = "academia-bid.development-user";

export function DevelopmentUserSelector({ dark = false, compact = false }: { dark?: boolean; compact?: boolean }) {
  const [users, setUsers] = useState<DevelopmentUser[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [label, setLabel] = useState("Cargando usuario…");

  useEffect(() => {
    const savedId = window.localStorage.getItem(storageKey) ?? undefined;
    Promise.all([getDevelopmentUsers(), getCurrentUser(savedId)])
      .then(([availableUsers, currentUser]) => {
        setUsers(availableUsers);
        setSelectedId(currentUser.external_id);
        setLabel(`${currentUser.name} · ${currentUser.role}`);
      })
      .catch(() => setLabel("Backend no disponible"));
  }, []);

  function changeUser(externalId: string) {
    window.localStorage.setItem(storageKey, externalId);
    setSelectedId(externalId);
    const selectedUser = users.find((user) => user.external_id === externalId);
    setLabel(selectedUser ? `${selectedUser.name} · ${selectedUser.role}` : "Usuario de desarrollo");
    window.location.reload();
  }

  return (
    <label className={`flex items-center gap-2 text-sm ${compact ? "flex-col items-stretch" : ""} ${dark ? "text-white/60" : "text-slate-600"}`}>
      <span className={compact ? "hidden" : "hidden sm:inline"}>Usuario actual:</span>
      <select
        aria-label="Usuario de desarrollo actual"
        className={`rounded border px-2 py-1 ${compact ? "w-full" : ""} ${dark ? "border-white/20 bg-white/10 text-white" : "border-slate-300 bg-white text-slate-900"}`}
        value={selectedId}
        onChange={(event) => changeUser(event.target.value)}
      >
        {!selectedId && <option value="">{label}</option>}
        {users.map((user) => <option key={user.id} value={user.external_id}>{user.name} ({user.role})</option>)}
      </select>
    </label>
  );
}
