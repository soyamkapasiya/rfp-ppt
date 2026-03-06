import { useState } from "react";
import { DeckPreview } from "../components/DeckPreview";
import { ExportCenter } from "../components/ExportCenter";
import { GenerationConsole } from "../components/GenerationConsole";
import { NewProjectForm } from "../components/NewProjectForm";
import { QuestionBank } from "../components/QuestionBank";
import { ScreenTabs } from "../components/ScreenTabs";

type Screen = "new" | "console" | "questions" | "preview" | "export";

export function App() {
  const [activeScreen, setActiveScreen] = useState<Screen>("new");
  const [jobId, setJobId] = useState<string | null>(null);

  return (
    <main className="container">
      <h1>RFP AI Platform</h1>
      <ScreenTabs active={activeScreen} onChange={setActiveScreen} />

      {activeScreen === "new" && (
        <NewProjectForm
          onCreated={(id) => {
            setJobId(id);
            setActiveScreen("console");
          }}
        />
      )}

      {activeScreen === "console" && <GenerationConsole jobId={jobId} />}
      {activeScreen === "questions" && <QuestionBank jobId={jobId} />}
      {activeScreen === "preview" && <DeckPreview jobId={jobId} />}
      {activeScreen === "export" && <ExportCenter jobId={jobId} />}
    </main>
  );
}
