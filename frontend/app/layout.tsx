import type { Metadata } from "next";
import { AppHeader } from "@/components/app-header";
import { AchievementsProvider } from "@/components/achievements-overlay";
import { EntraSession } from "@/components/entra-session";
import "./globals.css";

export const metadata: Metadata = {
  title: "Academia BID",
  description: "Plataforma interna de capacitación corporativa",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body><EntraSession><AchievementsProvider><AppHeader /><div className="min-h-screen pt-14 md:pl-64 md:pt-0">{children}</div></AchievementsProvider></EntraSession></body>
    </html>
  );
}
