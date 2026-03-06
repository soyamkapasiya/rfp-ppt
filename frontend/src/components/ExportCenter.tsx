type Props = { jobId: string | null };

export function ExportCenter({ jobId }: Props) {
  const apiBase = "http://localhost:8000/api/v1";
  const key = "editor-local-key";

  if (!jobId) {
    return (
      <section className="card">
        <h2>Export Center</h2>
        <p>Create a job first.</p>
      </section>
    );
  }

  const pptUrl = `${apiBase}/generation/jobs/${jobId}/artifacts/deck?x-api-key=${key}`;

  return (
    <section className="card">
      <h2>Export Center</h2>
      <p><a href={pptUrl} target="_blank">Download deck.pptx</a></p>
      <p>Sources, questions, and reports are available through API artifact endpoints.</p>
    </section>
  );
}
