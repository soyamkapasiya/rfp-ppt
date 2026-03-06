import { FormEvent, useState } from "react";
import { createGenerationJob } from "../lib/api";

type Props = {
  onCreated: (jobId: string) => void;
};

export function NewProjectForm({ onCreated }: Props) {
  const [projectName, setProjectName] = useState("");
  const [industry, setIndustry] = useState("");
  const [region, setRegion] = useState("");
  const [requirementText, setRequirementText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const data = await createGenerationJob({
        project_name: projectName,
        industry,
        region,
        requirement_text: requirementText,
      });
      onCreated(data.job_id);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="card">
      <h2>New Project</h2>
      <label>Project Name<input value={projectName} onChange={(e) => setProjectName(e.target.value)} required /></label>
      <label>Industry<input value={industry} onChange={(e) => setIndustry(e.target.value)} /></label>
      <label>Region<input value={region} onChange={(e) => setRegion(e.target.value)} /></label>
      <label>
        Requirement Text
        <textarea value={requirementText} onChange={(e) => setRequirementText(e.target.value)} minLength={40} required />
      </label>
      <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Submitting..." : "Generate RFP PPT"}</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
