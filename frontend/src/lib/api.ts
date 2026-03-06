export type RequirementInput = {
  project_name: string;
  industry?: string;
  region?: string;
  requirement_text: string;
};

export type JobStatus = {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  stage: string;
  artifacts: Record<string, unknown>;
  error?: string | null;
};

const API_BASE = "http://localhost:8000/api/v1";
const API_KEY = "editor-local-key";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(init?.headers || {})
    }
  });

  if (!res.ok) {
    throw new Error(`API error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function createGenerationJob(payload: RequirementInput): Promise<{ job_id: string; status: string }> {
  return request("/generation/rfp-ppt", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function getJob(jobId: string): Promise<JobStatus> {
  return request(`/generation/jobs/${jobId}`, { method: "GET" });
}

export async function getArtifact(jobId: string, artifactName: string): Promise<any> {
  return request(`/generation/jobs/${jobId}/artifacts/${artifactName}`, { method: "GET" });
}
