import { CatalogView } from "@/components/catalog-view";

export default function AcademiesPage() {
  return <main className="mx-auto max-w-6xl px-6 py-10"><section className="app-gradient rounded-2xl p-6 text-white"><p className="text-sm text-cyan-200">Centro de aprendizaje</p><h1 className="mt-1 text-3xl font-bold">Catálogo de academias</h1><p className="mt-2 text-sm text-white/70">Unidades de negocio disponibles.</p></section><div className="mt-6"><CatalogView /></div></main>;
}
