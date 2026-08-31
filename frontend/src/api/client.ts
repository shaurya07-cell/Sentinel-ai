import { AnalysisResponse } from "../types";

const BASE_URL = "/api";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function runDemo(): Promise<AnalysisResponse> {
  const res = await fetch(`${BASE_URL}/demo/run`, { method: "POST" });
  if (!res.ok) {
    const body = await safeJson(res);
    throw new ApiError(body?.detail ?? "Failed to run demo scenario.", res.status);
  }
  return res.json();
}

export async function analyzeProject(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/project/analyze`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await safeJson(res);
    throw new ApiError(body?.detail ?? "Failed to analyze project.", res.status);
  }
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

async function safeJson(res: Response): Promise<any> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}
