type Props = {
  active: string;
  onChange: (id: "new" | "console" | "questions" | "preview" | "export") => void;
};

const tabs = [
  { id: "new", label: "New Project" },
  { id: "console", label: "Generation Console" },
  { id: "questions", label: "Question Bank" },
  { id: "preview", label: "Deck Preview" },
  { id: "export", label: "Export Center" }
] as const;

export function ScreenTabs({ active, onChange }: Props) {
  return (
    <div className="tabs">
      {tabs.map((tab) => (
        <button key={tab.id} className={active === tab.id ? "tab active" : "tab"} onClick={() => onChange(tab.id)}>
          {tab.label}
        </button>
      ))}
    </div>
  );
}
