import { FormEvent, useState } from "react";
import { useJobPolling } from "../hooks/useJobPolling";
import { createGenerationJob } from "../lib/api";

export function App() {
  const [projectName, setProjectName] = useState("");
  const [industry, setIndustry] = useState("");
  const [region, setRegion] = useState("");
  const [requirementText, setRequirementText] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const { job, error } = useJobPolling(jobId);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    try {
      const created = await createGenerationJob({
        project_name: projectName,
        industry,
        region,
        requirement_text: requirementText
      });
      setJobId(created.job_id);
    } catch (err) {
      setSubmitError((err as Error).message);
    }
  }

  return (
    <main className="container">
      <h1>RFP AI Project Generator</h1>
      <form onSubmit={onSubmit} className="card">
        <label>
          Project Name
          <input value={projectName} onChange={(e) => setProjectName(e.target.value)} required />
        </label>
        <label>
          Industry
          <input value={industry} onChange={(e) => setIndustry(e.target.value)} />
        </label>
        <label>
          Region
          <input value={region} onChange={(e) => setRegion(e.target.value)} />
        </label>
        <label>
          Requirement Text
          <textarea value={requirementText} onChange={(e) => setRequirementText(e.target.value)} minLength={40} required />
        </label>
        <button type="submit">Generate RFP PPT</button>
      </form>

      {submitError && <p className="error">{submitError}</p>}
      {error && <p className="error">{error}</p>}

      {jobId && (
        <section className="card">
          <h2>Generation Console</h2>
          <p><strong>Job ID:</strong> {jobId}</p>
          <p><strong>Status:</strong> {job?.status ?? "queued"}</p>
          <p><strong>Stage:</strong> {job?.stage ?? "queued"}</p>
          {job?.artifacts?.pptx_path && <p><strong>PPT:</strong> {job.artifacts.pptx_path}</p>}
        </section>
      )}
    </main>
  );
}
