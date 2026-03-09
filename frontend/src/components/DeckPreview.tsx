import { useEffect, useState } from "react";
import { getArtifact, type QualityReport } from "../lib/api";

type Props = { jobId: string | null };

type SlideSpec = {
  title: string;
  objective: string;
  bullets: string[];
  references: string[];
};

function ScoreRing({ score, label }: { score: number; label: string }) {
  const numClass =
    score >= 75 ? "score-number-good" : score >= 50 ? "score-number-medium" : "score-number-bad";
  const barClass =
    score >= 75
      ? "progress-bar-success"
      : score >= 50
        ? "progress-bar-amber"
        : "progress-bar-danger";

  return (
    <div className="score-card">
      <div className="score-label">{label}</div>
      <div className={`score-number ${numClass}`}>{score}</div>
      <div className="progress-container">
        <div
          className={`progress-bar ${barClass}`}
          style={{ width: `${score}%` }}
          role="progressbar"
          aria-valuenow={score}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
    </div>
  );
}

export function DeckPreview({ jobId }: Props) {
  const [report, setReport] = useState<QualityReport | null>(null);
  const [slides, setSlides] = useState<SlideSpec[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setReport(null);
      setSlides([]);
      setError(null);
      return;
    }

    let active = true;
    setIsLoading(true);
    setError(null);

    const fetchAll = async () => {
      try {
        const [reportResp] = await Promise.allSettled([
          getArtifact<QualityReport>(jobId, "quality_report"),
        ]);

        if (!active) return;

        if (reportResp.status === "fulfilled") {
          setReport(reportResp.value.data ?? null);
        } else {
          setError((reportResp.reason as Error).message);
        }
      } finally {
        if (active) setIsLoading(false);
      }
    };

    fetchAll();
    return () => { active = false; };
  }, [jobId]);

  if (!jobId) {
    return (
      <div className="card animate-fade-in">
        <div className="empty-state">
          <div className="empty-icon">🖥️</div>
          <div className="empty-title">No job selected</div>
          <div className="empty-desc">
            Create a project to preview the generated deck quality report.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Quality Report */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">📊</span>
            Quality Report
          </h2>
          {report && (
            <span className={`badge ${report.pass_gate ? "badge-completed" : "badge-failed"}`}>
              {report.pass_gate ? "✅ Pass" : "❌ Fail"}
            </span>
          )}
        </div>

        {isLoading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div className="skeleton" style={{ height: 24, width: "60%" }} />
            <div className="skeleton" style={{ height: 100 }} />
          </div>
        )}

        {error && (
          <div className="error-block" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {!isLoading && !report && !error && (
          <div className="empty-state" style={{ padding: "32px 0" }}>
            <div className="empty-icon">⏳</div>
            <div className="empty-title">Report not yet available</div>
            <div className="empty-desc">
              The quality report will appear after the pipeline completes.
            </div>
          </div>
        )}

        {report && (
          <>
            {/* Overall score summary */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                padding: "16px 20px",
                background: "rgba(255,255,255,0.025)",
                borderRadius: "var(--r-md)",
                border: "1px solid var(--c-border)",
                marginBottom: 20,
              }}
            >
              <div
                style={{
                  fontSize: 52,
                  fontWeight: 800,
                  letterSpacing: "-0.04em",
                  lineHeight: 1,
                  color:
                    report.overall_score >= 75
                      ? "var(--c-emerald)"
                      : report.overall_score >= 50
                        ? "var(--c-amber)"
                        : "var(--c-rose)",
                }}
              >
                {report.overall_score}
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: "var(--c-text)" }}>
                  Overall Score
                </div>
                <div style={{ fontSize: 13, color: "var(--c-text-muted)", marginTop: 2 }}>
                  Quality gate:{" "}
                  <strong
                    style={{ color: report.pass_gate ? "var(--c-emerald)" : "var(--c-rose)" }}
                  >
                    {report.pass_gate ? "Passed" : "Failed"}
                  </strong>
                </div>
              </div>
            </div>

            {/* Score breakdown */}
            <div className="score-grid">
              <ScoreRing score={report.clarity_score} label="Clarity" />
              <ScoreRing score={report.evidence_score} label="Evidence" />
              <ScoreRing score={report.feasibility_score} label="Feasibility" />
              <ScoreRing score={report.executive_readability_score} label="Readability" />
            </div>

            {/* Issues */}
            {report.issues && report.issues.length > 0 && (
              <div style={{ marginTop: 20 }}>
                <div
                  style={{
                    fontWeight: 600,
                    fontSize: 13,
                    color: "var(--c-text)",
                    marginBottom: 10,
                  }}
                >
                  Issues Found
                </div>
                <ul
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    paddingLeft: 0,
                    listStyle: "none",
                  }}
                >
                  {report.issues.map((issue, i) => (
                    <li
                      key={i}
                      style={{
                        display: "flex",
                        gap: 8,
                        alignItems: "flex-start",
                        fontSize: 13,
                        color: "var(--c-text-muted)",
                      }}
                    >
                      <span style={{ color: "var(--c-rose)", flexShrink: 0 }}>▸</span>
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {/* Premium Generation Trigger */}
            <div style={{ marginTop: 30, paddingTop: 20, borderTop: "1px solid var(--c-border)", textAlign: "center" }}>
              <button
                className="btn btn-primary btn-lg"
                onClick={async () => {
                  if (!jobId) return;
                  setIsLoading(true);
                  try {
                    const res = await fetch(`http://localhost:8001/api/v1/generation/jobs/${jobId}/generate-premium`, {
                      method: "POST",
                      headers: { "X-API-Key": "editor-local-key" },
                    });
                    if (res.ok) {
                      alert("Premium generation started! Manus AI is rendering your slides...");
                    } else {
                      throw new Error("Failed to start premium generation");
                    }
                  } catch (err) {
                    setError("Failed to trigger premium generation");
                  } finally {
                    setIsLoading(false);
                  }
                }}
              >
                ✨ Generate Premium Manus Deck
              </button>
              <p style={{ marginTop: 10, fontSize: 12, color: "var(--c-text-muted)" }}>
                This will trigger Manus AI to render a high-fidelity PPTX with your confirmed strategy.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
