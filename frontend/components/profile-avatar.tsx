"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api/client";

function initials(name: string) {
  return name.split(" ").filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

export function ProfileAvatar({ name }: { name: string }) {
  const [photoUrl, setPhotoUrl] = useState("");

  useEffect(() => {
    let objectUrl = "";
    apiFetch("/api/me/photo").then(async (response) => {
      if (!response.ok || response.status === 204) return;
      objectUrl = URL.createObjectURL(await response.blob());
      setPhotoUrl(objectUrl);
    }).catch(() => undefined);
    return () => { if (objectUrl) URL.revokeObjectURL(objectUrl); };
  }, []);

  if (photoUrl) return <img alt={`Foto de ${name}`} className="h-16 w-16 rounded-full border-2 border-white/40 object-cover shadow-lg" src={photoUrl} />;
  return <span aria-label={`Iniciales de ${name}`} className="flex h-16 w-16 items-center justify-center rounded-full border-2 border-white/30 bg-white/15 text-lg font-bold text-white">{initials(name)}</span>;
}
