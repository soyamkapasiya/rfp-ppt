import { useEffect, useRef, useState } from "react";
import { useJobPolling } from "../hooks/useJobPolling";

type Props = {
  jobId: string | null;
};

type StageInfo = {
  key: string;
  label: string;
  icon: string;
  desc: string;
};

const PIPELINE_STAGES: StageInfo[] = [
  { key: "queued", label: "Queued", icon: "⏳", desc: "Job accepted, waiting for worker" },
  { key: "pipeline", label: "Running Pipeline", icon: "⚙️", desc: "AI pipeline executing" },
  { key: "qa", label: "Quality Gate", icon: "🔍", desc: "Evaluating output quality" },
  { key: "completed", label: "Completed", icon: "✅", desc: "Deck ready to export" },
];

function getStageIndex(stage: string): number {
  const idx = PIPELINE_STAGES.findIndex((s) => s.key === stage);
  return idx >= 0 ? idx : 0;
}

function nowStr(): string {
  return new Date().toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

type LogEntry = { time: string; msg: string; type: string };

const STATUS_PROGRESS: Record<string, number> = {
  queued: 5,
  processing: 60,
  completed: 100,
  failed: 100,
};

const STAGE_DESC: Record<string, string> = {
  queued: "Job queued — worker will pick it up shortly",
  pipeline: "Running AI pipeline: research → questions → slides → quality check",
  qa: "Evaluating quality gate…",
  failed: "Pipeline encountered an error",
  completed: "Pipeline completed successfully",
};

export function GenerationConsole({ jobId }: Props) {
  const { data, isLoading, error } = useJobPolling(jobId);

  // Local log buffer (not state to avoid extra re-renders)
  const logRef = useRef<LogEntry[]>([]);
  const prevStage = useRef<string>("");
  const prevStatus = useRef<string>("");

  // Force re-render when log changes
  const [, setTick] = useState(0);
  const bump = () => setTick((n) => n + 1);

  useEffect(() => {
    if (!data) return;

    let changed = false;

    if (data.stage !== prevStage.current || data.status !== prevStatus.current) {
      prevStage.current = data.stage;
      prevStatus.current = data.status;
      logRef.current = [
        ...logRef.current,
        {
          time: nowStr(),
          msg: STAGE_DESC[data.stage] ?? `Stage: ${data.stage}`,
          type: data.status,
        },
      ];
      changed = true;
    }

    if (data.error) {
      const last = logRef.current[logRef.current.length - 1];
      if (last?.msg !== `Error: ${data.error}`) {
        logRef.current = [
          ...logRef.current,
          { time: nowStr(), msg: `Error: ${data.error}`, type: "failed" },
        ];
        changed = true;
      }
    }

    if (changed) bump();
  }, [data?.stage, data?.status, data?.error]); // eslint-disable-line react-hooks/exhaustive-deps

  const status = data?.status ?? "idle";
  const stage = data?.stage ?? "";
  const progress = STATUS_PROGRESS[status] ?? 0;
  const stageIdx = getStageIndex(stage);
  const isFailed = status === "failed";
  const isDone = status === "completed";

  const progressBarClass = isFailed ? "progress-bar-danger" : isDone ? "progress-bar-success" : "progress-bar-primary";

  if (!jobId) {
    return (
      <div className="card animate-fade-in">
        <div className="empty-state">
          <div className="empty-icon">🚀</div>
          <div className="empty-title">No job running</div>
          <div className="empty-desc">
            Create a new project to start the RFP generation pipeline.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Status Overview */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">⚡</span>
            Generation Console
          </h2>
          <span className={`badge badge-${status === "idle" ? "idle" : status}`}>
            {status === "idle" ? "Idle" : status}
          </span>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-label">Job ID</div>
            <div className="stat-value font-mono" style={{ fontSize: 13 }}>
              {jobId.slice(0, 8)}…
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Status</div>
            <div className="stat-value" style={{ fontSize: 16, textTransform: "capitalize" }}>
              {status}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Stage</div>
            <div className="stat-value" style={{ fontSize: 16, textTransform: "capitalize" }}>
              {stage || "—"}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Progress</div>
            <div className="stat-value">{progress}%</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="progress-container mt-3">
          <div
            className={`progress-bar ${progressBarClass}`}
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>

        {error && (
          <div className="error-block mt-3" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Pipeline timeline */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">🗺️</span>
            Pipeline Stages
          </h2>
        </div>
        <div className="timeline">
          {PIPELINE_STAGES.map((s, idx) => {
            const errorHere = isFailed && s.key === stage;
            const done = !isFailed && (idx < stageIdx || isDone);
            const active = !isFailed && !isDone && idx === stageIdx;
            const dotClass = errorHere ? "error" : done ? "done" : active ? "active" : "";
            const dotIcon = errorHere ? "✖" : done ? "✓" : s.icon;
            return (
              <div key={s.key} className="timeline-item">
                <div className={`timeline-dot ${dotClass}`}>{dotIcon}</div>
                <div className="timeline-body">
                  <div className="timeline-title">{s.label}</div>
                  <div className="timeline-subtitle">{s.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live log */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">🖥️</span>
            Live Log
          </h2>
          {isLoading && (
            <span className="text-xs text-muted flex items-center gap-2">
              <span
                className="btn-spinner"
                style={{ borderTopColor: "var(--c-primary-light)", width: 12, height: 12 }}
              />
              polling…
            </span>
          )}
        </div>
        <div className="console-box" id="console-log" role="log" aria-live="polite">
          {logRef.current.length === 0 ? (
            <span className="text-faint">Waiting for events…</span>
          ) : (
            logRef.current.map((entry, i) => (
              <div key={i} className="console-line">
                <span className="console-time">[{entry.time}]</span>
                <span className={`console-msg-${entry.type}`}>{entry.msg}</span>
              </div>
            ))
          )}
          {!isDone && !isFailed && (
            <div className="console-line">
              <span className="console-time">[…]</span>
              <span className="console-msg-info">
                <span className="console-cursor" />
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
