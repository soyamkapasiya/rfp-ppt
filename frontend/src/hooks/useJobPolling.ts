// ─── Job polling hook ─────────────────────────────────────────────────────────
import { useEffect, useRef, useState } from "react";
import { getJob, type JobRecord, type JobStatus } from "../lib/api";

const POLL_INTERVAL_MS = 2500;
const TERMINAL_STATES: JobStatus[] = ["completed", "failed"];

export type JobPollingState = {
  data: JobRecord | null;
  isLoading: boolean;
  error: string | null;
};

export function useJobPolling(jobId: string | null): JobPollingState {
  const [data, setData] = useState<JobRecord | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Keep a stable ref to the interval so we can clear it without
  // the effect re-running on every render.
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!jobId) {
      setData(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    let mounted = true;

    const clearTimer = () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };

    const fetchOnce = async () => {
      try {
        const result = await getJob(jobId);
        if (!mounted) return;
        setData(result);
        setError(null);
        // Stop polling once we reach a terminal state
        if (TERMINAL_STATES.includes(result.status)) {
          clearTimer();
        }
      } catch (e) {
        if (!mounted) return;
        setError((e as Error).message);
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    setIsLoading(true);
    fetchOnce();
    timerRef.current = setInterval(fetchOnce, POLL_INTERVAL_MS);

    return () => {
      mounted = false;
      clearTimer();
    };
  }, [jobId]);

  return { data, isLoading, error };
}
