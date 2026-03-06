import { useEffect, useState } from "react";
import { getJob } from "../lib/api";

export function useJobPolling(jobId: string | null) {
  const [job, setJob] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let active = true;
    const timer = setInterval(async () => {
      try {
        const data = await getJob(jobId);
        if (!active) return;
        setJob(data);
        if (["completed", "failed"].includes(data.status)) clearInterval(timer);
      } catch (e) {
        setError((e as Error).message);
      }
    }, 2500);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [jobId]);

  return { job, error };
}
