import { useEffect, useState } from "react";
import { getArtifact, type QuestionItem } from "../lib/api";

type Props = { jobId: string | null };

const CATEGORY_COLORS: Record<string, string> = {
  functional: "var(--c-primary-light)",
  technical: "var(--c-teal-light)",
  security: "var(--c-rose)",
  compliance: "var(--c-amber)",
  data: "var(--c-violet)",
  timeline: "var(--c-emerald)",
  budget: "#f97316",
  operations: "#a78bfa",
};

const CATEGORY_BG: Record<string, string> = {
  functional: "rgba(59,130,246,0.1)",
  technical: "rgba(13,148,136,0.1)",
  security: "rgba(244,63,94,0.1)",
  compliance: "rgba(245,158,11,0.1)",
  data: "rgba(124,58,237,0.1)",
  timeline: "rgba(16,185,129,0.1)",
  budget: "rgba(249,115,22,0.1)",
  operations: "rgba(167,139,250,0.1)",
};

const PRIORITY_LABELS: Record<string, string> = {
  high: "🔴 High",
  medium: "🟡 Medium",
  low: "🟢 Low",
};

const ALL_FILTER = "__all__";

export function QuestionBank({ jobId }: Props) {
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>(ALL_FILTER);
  const [priorityFilter, setPriorityFilter] = useState<string>(ALL_FILTER);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!jobId) {
      setQuestions([]);
      setError(null);
      return;
    }

    let active = true;
    setIsLoading(true);
    setError(null);

    getArtifact<QuestionItem[]>(jobId, "questions")
      .then((resp) => {
        if (active) setQuestions(resp.data ?? []);
      })
      .catch((err) => {
        if (active) setError((err as Error).message);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => { active = false; };
  }, [jobId]);

  const categories = [ALL_FILTER, ...Array.from(new Set(questions.map((q) => q.category)))];
  const priorities = [ALL_FILTER, "high", "medium", "low"];

  const filtered = questions.filter((q) => {
    const catOk = filter === ALL_FILTER || q.category === filter;
    const priOk = priorityFilter === ALL_FILTER || q.priority === priorityFilter;
    const termOk = search === "" || q.question.toLowerCase().includes(search.toLowerCase());
    return catOk && priOk && termOk;
  });

  if (!jobId) {
    return (
      <div className="card animate-fade-in">
        <div className="empty-state">
          <div className="empty-icon">❓</div>
          <div className="empty-title">No active job</div>
          <div className="empty-desc">Start a project to generate clarifying questions.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <span className="card-title-icon">💬</span>
            Question Bank
          </h2>
          {questions.length > 0 && (
            <span className="badge badge-processing">{questions.length} questions</span>
          )}
        </div>

        {isLoading && (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton" style={{ height: 80, borderRadius: 12 }} />
            ))}
          </div>
        )}

        {error && (
          <div className="error-block" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {!isLoading && !error && questions.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">⏳</div>
            <div className="empty-title">Questions not yet available</div>
            <div className="empty-desc">
              Wait for the pipeline to complete the question mining stage.
            </div>
          </div>
        )}

        {!isLoading && questions.length > 0 && (
          <>
            {/* Filters */}
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 20 }}>
              <input
                type="text"
                placeholder="Search questions…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ marginBottom: 0 }}
              />
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    className={`btn btn-sm ${filter === cat ? "btn-primary" : "btn-secondary"}`}
                    onClick={() => setFilter(cat)}
                  >
                    {cat === ALL_FILTER ? "All categories" : cat}
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {priorities.map((p) => (
                  <button
                    key={p}
                    type="button"
                    className={`btn btn-sm ${priorityFilter === p ? "btn-primary" : "btn-secondary"}`}
                    onClick={() => setPriorityFilter(p)}
                  >
                    {p === ALL_FILTER ? "All priorities" : PRIORITY_LABELS[p]}
                  </button>
                ))}
              </div>
            </div>

            <div className="question-list">
              {filtered.length === 0 ? (
                <div className="empty-state" style={{ padding: "30px 0" }}>
                  <div className="empty-title">No matches found</div>
                  <div className="empty-desc">Try different search terms or filters.</div>
                </div>
              ) : (
                filtered.map((q, idx) => (
                  <div key={idx} className="question-item">
                    <div className="question-meta">
                      <span
                        className="question-category"
                        style={{
                          color: CATEGORY_COLORS[q.category] ?? "var(--c-text-muted)",
                          background: CATEGORY_BG[q.category] ?? "rgba(255,255,255,0.06)",
                          borderColor: (CATEGORY_COLORS[q.category] ?? "var(--c-border)") + "44",
                        }}
                      >
                        {q.category}
                      </span>
                      {q.priority && (
                        <span
                          className={`question-category question-priority-${q.priority}`}
                          style={{ textTransform: "capitalize" }}
                        >
                          {PRIORITY_LABELS[q.priority]}
                        </span>
                      )}
                    </div>
                    <div className="question-text">{q.question}</div>
                    {q.reason && <div className="question-reason">{q.reason}</div>}
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
