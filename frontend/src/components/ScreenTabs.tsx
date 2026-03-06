type Screen = "new" | "console" | "questions" | "preview" | "export";

type TabDef = {
  id: Screen;
  label: string;
  icon: string;
  hint: string;
  requiresJob?: boolean;
};

const TABS: TabDef[] = [
  { id: "new", label: "New Project", icon: "➕", hint: "Create a new RFP generation job" },
  { id: "console", label: "Generation Console", icon: "⚡", hint: "Monitor pipeline progress", requiresJob: true },
  { id: "questions", label: "Question Bank", icon: "💬", hint: "View extracted questions", requiresJob: true },
  { id: "preview", label: "Quality Report", icon: "📊", hint: "Inspect quality scores", requiresJob: true },
  { id: "export", label: "Export Center", icon: "📦", hint: "Download all artifacts", requiresJob: true },
];

type Props = {
  active: Screen;
  onChange: (id: Screen) => void;
  hasJob: boolean;
};

export function ScreenTabs({ active, onChange, hasJob }: Props) {
  return (
    <nav
      className="sidebar"
      aria-label="Application navigation"
    >
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon" aria-hidden="true">✨</div>
        <div className="sidebar-logo-text">
          <span className="sidebar-logo-title">RFP AI Platform</span>
          <span className="sidebar-logo-subtitle">v0.2.0 – Proposal Generator</span>
        </div>
      </div>

      <div className="sidebar-section-label">Navigation</div>

      {TABS.map((tab) => {
        const disabled = !!(tab.requiresJob && !hasJob);
        return (
          <button
            key={tab.id}
            id={`nav-${tab.id}`}
            className={`nav-item ${active === tab.id ? "active" : ""}`}
            onClick={() => !disabled && onChange(tab.id)}
            disabled={disabled}
            aria-current={active === tab.id ? "page" : undefined}
            title={disabled ? "Create a project first" : tab.hint}
            style={{ opacity: disabled ? 0.4 : 1, cursor: disabled ? "not-allowed" : "pointer" }}
          >
            <span className="nav-item-icon">{tab.icon}</span>
            {tab.label}
            {active === tab.id && (
              <span className="nav-item-badge">Active</span>
            )}
          </button>
        );
      })}

      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className="status-dot" />
          Backend connected
        </div>
        <div className="sidebar-status" style={{ paddingTop: 0, fontSize: 11 }}>
          <span style={{ width: 7 }} />
          {import.meta.env.VITE_API_BASE?.split("/")[2] || "localhost:8001"}
        </div>
      </div>
    </nav>
  );
}

export type { Screen };
