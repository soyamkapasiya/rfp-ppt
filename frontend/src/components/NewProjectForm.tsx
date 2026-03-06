import { type FormEvent, useState } from "react";
import { createGenerationJob } from "../lib/api";
import { useToast } from "../lib/toast";

const INDUSTRIES = [
  "Healthcare & Life Sciences",
  "Financial Services & Banking",
  "Government & Public Sector",
  "Defence & Aerospace",
  "Information Technology",
  "Telecommunications",
  "Energy & Utilities",
  "Construction & Infrastructure",
  "Education",
  "Retail & E-commerce",
  "Manufacturing",
  "Other",
];

const REGIONS = [
  "North America",
  "Europe",
  "Asia-Pacific",
  "Middle East & Africa",
  "Latin America",
  "United Kingdom",
  "Australia & New Zealand",
  "Global",
];

type Props = {
  onCreated: (jobId: string) => void;
};

export function NewProjectForm({ onCreated }: Props) {
  const { toast } = useToast();

  const [projectName, setProjectName] = useState("");
  const [industry, setIndustry] = useState("");
  const [region, setRegion] = useState("");
  const [requirementText, setRequirementText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const charCount = requirementText.length;
  const MIN_CHARS = 40;
  const isValid = projectName.trim().length > 0 && charCount >= MIN_CHARS;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!isValid) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const data = await createGenerationJob({
        project_name: projectName.trim(),
        industry: industry || undefined,
        region: region || undefined,
        requirement_text: requirementText.trim(),
      });
      toast("success", "Job created!", `Job ID: ${data.job_id}`);
      onCreated(data.job_id);
    } catch (err) {
      const msg = (err as Error).message;
      setError(msg);
      toast("error", "Failed to create job", msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="animate-fade-in" noValidate>
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">📋</span>
            Project Details
          </h2>
        </div>
        <p className="card-desc">
          Provide your RFP requirements and we'll generate a professional
          PowerPoint proposal deck using AI.
        </p>

        {/* Project Name */}
        <div className="form-group">
          <label htmlFor="project-name" className="form-label">
            Project Name
            <span className="form-label-required">* required</span>
          </label>
          <input
            id="project-name"
            type="text"
            placeholder="e.g. NHS Digital Transformation Initiative"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
            autoComplete="off"
            maxLength={200}
          />
        </div>

        {/* Industry + Region row */}
        <div className="form-row">
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="industry" className="form-label">
              Industry
            </label>
            <select
              id="industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
            >
              <option value="">Select industry…</option>
              {INDUSTRIES.map((i) => (
                <option key={i} value={i}>
                  {i}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="region" className="form-label">
              Region
            </label>
            <select
              id="region"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
            >
              <option value="">Select region…</option>
              {REGIONS.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">📄</span>
            Requirement Text
          </h2>
          <span
            className={`text-xs font-mono ${charCount >= MIN_CHARS ? "text-success" : "text-muted"}`}
          >
            {charCount} / {MIN_CHARS}+ chars
          </span>
        </div>

        <textarea
          id="requirement-text"
          placeholder="Paste your RFP excerpt or describe your project requirements in detail. Include objectives, constraints, budget range, and any compliance requirements…"
          value={requirementText}
          onChange={(e) => setRequirementText(e.target.value)}
          minLength={MIN_CHARS}
          required
          style={{ minHeight: 200 }}
        />
        <p className="form-hint">
          Minimum {MIN_CHARS} characters. More context yields better results.
        </p>

        {error && (
          <div className="error-block" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div style={{ marginTop: 20 }}>
          <button
            id="generate-btn"
            type="submit"
            className="btn btn-primary btn-lg btn-full"
            disabled={isSubmitting || !isValid}
          >
            {isSubmitting ? (
              <>
                <span className="btn-spinner" />
                Submitting…
              </>
            ) : (
              <>✨ Generate RFP Proposal Deck</>
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
