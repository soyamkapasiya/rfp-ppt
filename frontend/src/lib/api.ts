// ─── API Client ───────────────────────────────────────────────────────────────
// Centralises all calls to the RFP AI backend.
// Base URL and API key are read from Vite env variables so they can be
// overridden per environment without changing source code.

export type RequirementInput = {
  project_name: string;
  industry?: string;
  region?: string;
  requirement_text: string;
};

export type JobStatus = "queued" | "processing" | "completed" | "failed";

export type JobRecord = {
  job_id: string;
  status: JobStatus;
  stage: string;
  artifacts: Record<string, unknown>;
  error?: string | null;
};

export type QuestionItem = {
  question: string;
  category: string;
  reason?: string;
  priority?: "high" | "medium" | "low";
};

export type QualityReport = {
  clarity_score: number;
  evidence_score: number;
  feasibility_score: number;
  executive_readability_score: number;
  overall_score: number;
  pass_gate: boolean;
  issues: string[];
};

export type ApiErrorPayload = {
  detail: string | { msg: string; type: string }[];
};

// ── Configuration ────────────────────────────────────────────────────────────
const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  "http://localhost:8000/api/v1";

const API_KEY =
  (import.meta.env.VITE_API_KEY as string | undefined) ??
  "editor-local-key";

// ── Core fetch wrapper ────────────────────────────────────────────────────────
class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        ...(init?.headers ?? {}),
      },
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const body: ApiErrorPayload = await res.json();
        if (typeof body.detail === "string") {
          detail = body.detail;
        } else if (Array.isArray(body.detail)) {
          detail = body.detail.map((d) => d.msg).join("; ");
        }
      } catch {
        // ignore JSON parse errors on error body
      }
      throw new ApiError(res.status, detail);
    }

    return res.json() as Promise<T>;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === "AbortError") {
      throw new ApiError(408, "Request timed out – is the backend running?");
    }
    throw new ApiError(0, (err as Error).message ?? "Network error");
  }
}

// ── Endpoints ─────────────────────────────────────────────────────────────────
export async function createGenerationJob(
  payload: RequirementInput
): Promise<{ job_id: string; status: string }> {
  return request("/generation/rfp-ppt", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getJob(jobId: string): Promise<JobRecord> {
  return request(`/generation/jobs/${jobId}`, { method: "GET" });
}

export async function getArtifact<T = unknown>(
  jobId: string,
  artifactName: string
): Promise<{ job_id: string; artifact: string; data: T }> {
  return request(`/generation/jobs/${jobId}/artifacts/${artifactName}`, {
    method: "GET",
  });
}

/** Returns a direct download URL for binary artifacts (e.g. deck.pptx). */
export function getArtifactDownloadUrl(
  jobId: string,
  artifactName: string
): string {
  return `${API_BASE}/generation/jobs/${jobId}/artifacts/${artifactName}?x-api-key=${API_KEY}`;
}

export { ApiError };
