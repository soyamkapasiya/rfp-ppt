import { getArtifactDownloadUrl } from "../lib/api";

type Props = { jobId: string | null };

type ExportItem = {
  id: string;
  name: string;
  desc: string;
  artifact: string;
  icon: string;
  iconClass: string;
  ext: string;
  mime?: string;
};

const EXPORT_ITEMS: ExportItem[] = [
  {
    id: "deck",
    name: "Proposal Deck",
    desc: "Full AI-generated PowerPoint presentation",
    artifact: "deck",
    icon: "📊",
    iconClass: "export-item-icon-pptx",
    ext: "deck.pptx",
  },
  {
    id: "questions",
    name: "Question Bank",
    desc: "Clarifying questions extracted from the RFP",
    artifact: "questions",
    icon: "💬",
    iconClass: "export-item-icon-json",
    ext: "questions.json",
  },
  {
    id: "sources",
    name: "Research Sources",
    desc: "Web research documents used as evidence",
    artifact: "sources",
    icon: "📚",
    iconClass: "export-item-icon-json",
    ext: "sources.json",
  },
  {
    id: "quality_report",
    name: "Quality Report",
    desc: "Evaluation scores and identified issues",
    artifact: "quality_report",
    icon: "🔍",
    iconClass: "export-item-icon-json",
    ext: "quality_report.json",
  },
  {
    id: "claim_report",
    name: "Claim Verification",
    desc: "Fact-checking and claim verification results",
    artifact: "claim_report",
    icon: "✅",
    iconClass: "export-item-icon-json",
    ext: "claim_report.json",
  },
];

export function ExportCenter({ jobId }: Props) {
  if (!jobId) {
    return (
      <div className="card animate-fade-in">
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <div className="empty-title">Nothing to export yet</div>
          <div className="empty-desc">
            Complete a generation job to access all downloadable artifacts.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">📦</span>
            Export Center
          </h2>
        </div>
        <p className="card-desc">
          Download all artifacts generated for this job. Files are served directly from
          the backend.
        </p>

        <div className="export-list">
          {EXPORT_ITEMS.map((item) => {
            const url = getArtifactDownloadUrl(jobId, item.artifact);
            return (
              <div key={item.id} className="export-item">
                <div className="export-item-info">
                  <div className={`export-item-icon ${item.iconClass}`}>{item.icon}</div>
                  <div>
                    <div className="export-item-name">{item.name}</div>
                    <div className="export-item-desc">{item.desc}</div>
                  </div>
                </div>
                <a
                  id={`download-${item.id}`}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary btn-sm"
                  download={item.ext}
                >
                  ⬇ Download
                </a>
              </div>
            );
          })}
        </div>

        {/* Note about artifact availability */}
        <div
          style={{
            marginTop: 20,
            padding: "12px 16px",
            background: "rgba(59,130,246,0.06)",
            border: "1px solid rgba(59,130,246,0.18)",
            borderRadius: "var(--r-sm)",
            fontSize: 12,
            color: "var(--c-text-muted)",
          }}
        >
          ℹ️ Some files may not be available if the pipeline did not complete successfully.
          Check the Generation Console for details.
        </div>
      </div>
    </div>
  );
}
