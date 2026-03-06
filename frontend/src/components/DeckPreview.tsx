import { useEffect, useState } from "react";
import { getArtifact } from "../lib/api";

type Props = { jobId: string | null };

export function DeckPreview({ jobId }: Props) {
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    if (!jobId) {
      setReport(null);
      return;
    }

    let active = true;
    getArtifact(jobId, "quality_report").then((data) => {
      if (active) {
        setReport(data?.data || null);
      }
    });

    return () => {
      active = false;
    };
  }, [jobId]);

  return (
    <section className="card">
      <h2>Deck Preview</h2>
      {!jobId && <p>Create a job first.</p>}
      {report && (
        <>
          <p><strong>Overall Score:</strong> {report.overall_score}</p>
          <p><strong>Pass Gate:</strong> {String(report.pass_gate)}</p>
        </>
      )}
    </section>
  );
}
