import { useEffect, useState } from "react";
import { getJob, JobStatus } from "../lib/api";

export function useJobPolling(jobId: string | null) {
  const [data, setData] = useState<JobStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) {
      setData(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    let active = true;
    let timer: ReturnType<typeof setInterval> | null = null;

    const fetchOnce = async () => {
      setIsLoading(true);
      try {
        const result = await getJob(jobId);
        if (!active) {
          return;
        }
        setData(result);
        setError(null);

        if (result.status === "completed" || result.status === "failed") {
          if (timer) {
            clearInterval(timer);
            timer = null;
          }
        }
      } catch (e) {
        if (active) {
          setError((e as Error).message);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    fetchOnce();
    timer = setInterval(fetchOnce, 2500);

    return () => {
      active = false;
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [jobId]);

  return { data, isLoading, error };
}
