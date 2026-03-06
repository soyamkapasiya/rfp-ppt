export type RequirementInput = {
  project_name: string;
  industry?: string;
  region?: string;
  requirement_text: string;
};

const API_BASE = "http://localhost:8000/api/v1";

export async function createGenerationJob(payload: RequirementInput) {
  const res = await fetch(`${API_BASE}/generation/rfp-ppt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed to create generation job: ${res.status}`);
  return res.json();
}

export async function getJob(jobId: string) {
  const res = await fetch(`${API_BASE}/generation/jobs/${jobId}`);
  if (!res.ok) throw new Error(`Failed to fetch job: ${res.status}`);
  return res.json();
}
