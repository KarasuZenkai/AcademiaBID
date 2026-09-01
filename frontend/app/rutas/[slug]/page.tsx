"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getPath, type Course } from "@/lib/api/catalog";

export default function PathPage({ params }: { params: Promise<{ slug: string }> }) {
  const [name, setName] = useState(""); const [courses, setCourses] = useState<Course[]>([]);
  useEffect(() => { params.then(({ slug }) => getPath(slug).then((path) => { setName(path.name); setCourses(path.courses); })); }, [params]);
  return <main className="mx-auto max-w-4xl px-6 py-10"><section className="app-gradient rounded-2xl p-6 text-white"><p className="text-sm text-cyan-200">Ruta de aprendizaje</p><h1 className="mt-1 text-3xl font-bold">{name}</h1></section><div className="mt-6 grid gap-4 sm:grid-cols-2">{courses.map((course) => <Link className="app-card app-card-hover block overflow-hidden" href={`/cursos/${course.slug}`} key={course.slug}><div className="flex aspect-video items-center justify-center bg-gradient-to-br from-[#002952] to-[#51b1db] text-4xl text-white">▶</div><div className="p-5"><h2 className="font-semibold text-slate-800">{course.title}</h2><p className="mt-3 text-xs font-medium text-[#005a94]">{course.video_count} video{course.video_count === 1 ? "" : "s"} · {course.content_count} archivo{course.content_count === 1 ? "" : "s"}</p></div></Link>)}</div></main>;
}
