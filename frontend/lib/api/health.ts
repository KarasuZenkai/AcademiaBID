export type HealthStatus = {
  status: "ok" | "unavailable";
  database: "connected" | "unavailable";
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getHealth(): Promise<HealthStatus> {
  const response = await fetch(`${apiUrl}/health`);
  if (!response.ok) {
    throw new Error(`API health check failed with status ${response.status}`);
  }
  return response.json() as Promise<HealthStatus>;
}
