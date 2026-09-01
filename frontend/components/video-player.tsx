"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { getPlayback, saveVideoProgress, type Playback } from "@/lib/api/catalog";

function mergeRanges(ranges: Array<{ start: number; end: number }>) {
  return ranges.sort((left, right) => left.start - right.start).reduce<Array<{ start: number; end: number }>>((merged, item) => {
    const previous = merged[merged.length - 1];
    if (!previous || item.start > previous.end) merged.push({ ...item });
    else previous.end = Math.max(previous.end, item.end);
    return merged;
  }, []);
}

export function VideoPlayer({ lessonId, onCompleted, onEnded }: { lessonId: string; onCompleted?: () => void; onEnded?: () => void }) {
  const [playback, setPlayback] = useState<Playback | null>(null); const [error, setError] = useState("");
  const player = useRef<HTMLVideoElement>(null); const pending = useRef<Array<{ start: number; end: number }>>([]); const lastTime = useRef<number | null>(null); const lastCheckpoint = useRef(Date.now()); const sending = useRef(false); const completionNotified = useRef(false); const playbackEnded = useRef(false); const endNotified = useRef(false);
  useEffect(() => { getPlayback(lessonId).then(setPlayback).catch(() => setError("No se pudo preparar el video.")); }, [lessonId]);
  const addRange = useCallback((start: number, end: number) => { if (end > start && end - start <= 2.5) pending.current.push({ start, end }); }, []);
  const flush = useCallback(async () => {
    const video = player.current; if (!video || !playback || sending.current) return;
    const duration = Number.isFinite(video.duration) && video.duration > 0
      ? video.duration
      : video.seekable.length > 0
        ? video.seekable.end(video.seekable.length - 1)
        : playback.duration_seconds;
    if (!duration || !Number.isFinite(duration)) { setError("Aún no se pudo determinar la duración del video; vuelve a intentarlo en unos segundos."); return; }
    const ranges = mergeRanges(pending.current.splice(0)); sending.current = true;
    try { const result = await saveVideoProgress(lessonId, { position_seconds: video.currentTime, duration_seconds: duration, ranges, session_id: playback.session_id }); if (result.completed && !completionNotified.current) { completionNotified.current = true; onCompleted?.(); } if (result.completed && playbackEnded.current && !endNotified.current) { endNotified.current = true; onEnded?.(); } lastCheckpoint.current = Date.now(); }
    catch { pending.current.unshift(...ranges); setError("No se pudo guardar el progreso. Se reintentará al pausar."); }
    finally { sending.current = false; }
  }, [lessonId, onCompleted, onEnded, playback]);
  useEffect(() => { const onVisibility = () => { if (document.visibilityState === "hidden") void flush(); }; document.addEventListener("visibilitychange", onVisibility); window.addEventListener("pagehide", flush); return () => { document.removeEventListener("visibilitychange", onVisibility); window.removeEventListener("pagehide", flush); }; }, [flush]);
  if (error && !playback) return <p className="text-red-700">{error}</p>;
  if (!playback) return <p>Preparando video…</p>;
  const onTimeUpdate = () => { const now = player.current?.currentTime ?? 0; if (lastTime.current !== null) addRange(lastTime.current, now); lastTime.current = now; if (Date.now() - lastCheckpoint.current >= 30_000) void flush(); };
  const onPause = () => { const now = player.current?.currentTime ?? 0; if (lastTime.current !== null) addRange(lastTime.current, now); lastTime.current = now; void flush(); };
  const onLoaded = () => { if (player.current && playback.resume_position > 0) player.current.currentTime = playback.resume_position; };
  const handleEnded = () => { playbackEnded.current = true; onPause(); };
  return <video ref={player} className="mt-5 w-full rounded bg-black" controls preload="metadata" onLoadedMetadata={onLoaded} onPlay={() => { lastTime.current = player.current?.currentTime ?? 0; }} onPause={onPause} onSeeking={() => { lastTime.current = player.current?.currentTime ?? 0; }} onSeeked={() => { lastTime.current = player.current?.currentTime ?? 0; }} onTimeUpdate={onTimeUpdate} onEnded={handleEnded}><source src={playback.url} type="video/mp4" />Tu navegador no puede reproducir este video.</video>;
}
