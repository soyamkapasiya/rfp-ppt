import { useEffect, useState } from "react";
import { getArtifact } from "../lib/api";

type Props = { jobId: string | null };

export function QuestionBank({ jobId }: Props) {
  const [rows, setRows] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!jobId) {
      setRows([]);
      return;
    }

    let active = true;
    setIsLoading(true);
    getArtifact(jobId, "questions")
      .then((data) => {
        if (active) {
          setRows(data?.data || []);
        }
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [jobId]);

  return (
    <section className="card">
      <h2>Question Bank</h2>
      {!jobId && <p>Create a job first.</p>}
      {isLoading && <p>Loading questions...</p>}
      <ul>
        {rows.map((q, idx) => (
          <li key={idx}><strong>{q.category}:</strong> {q.question}</li>
        ))}
      </ul>
    </section>
  );
}
