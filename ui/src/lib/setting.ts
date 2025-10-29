import { fetchWithAuth } from "./api";

export interface Setting {
  isLocal: boolean;
  isApi: boolean;
  domainName: string | null;
  apiKey: string | null;
  modelName: string | null;
  temperature: number;
  systemPrompt: string | null;
}

export async function getSetting(): Promise<Setting | null> {
  const res = await fetchWithAuth("/setting");
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch setting");
  return res.json();
}

export async function createSetting(data: Partial<Setting>): Promise<Setting> {
  const res = await fetchWithAuth("/setting", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create setting");
  return res.json();
}

export async function updateSetting(data: Partial<Setting>): Promise<Setting> {
  const res = await fetchWithAuth("/setting", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update setting");
  return res.json();
}
