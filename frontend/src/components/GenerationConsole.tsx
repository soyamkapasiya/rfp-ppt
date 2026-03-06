import { useJobPolling } from "../hooks/useJobPolling";

type Props = {
  jobId: string | null;
};

export function GenerationConsole({ jobId }: Props) {
  const query = useJobPolling(jobId);

  return (
    <section className="card">
      <h2>Generation Console</h2>
      <p><strong>Job ID:</strong> {jobId ?? "Not started"}</p>
      <p><strong>Status:</strong> {query.data?.status ?? "idle"}</p>
      <p><strong>Stage:</strong> {query.data?.stage ?? "-"}</p>
      {query.data?.error && <p className="error">{query.data.error}</p>}
    </section>
  );
}
