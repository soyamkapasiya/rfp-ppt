import { useState } from "react";
import { DeckPreview } from "../components/DeckPreview";
import { ExportCenter } from "../components/ExportCenter";
import { GenerationConsole } from "../components/GenerationConsole";
import { NewProjectForm } from "../components/NewProjectForm";
import { QuestionBank } from "../components/QuestionBank";
import { ScreenTabs, type Screen } from "../components/ScreenTabs";
import { ToastContainer } from "../lib/toast";

const PAGE_META: Record<Screen, { title: string; subtitle: string }> = {
  new: { title: "New Project", subtitle: "Define your RFP requirements and start the AI generation pipeline." },
  console: { title: "Generation Console", subtitle: "Monitor the real-time progress of your generation job." },
  questions: { title: "Question Bank", subtitle: "AI-extracted clarifying questions to send back to the client." },
  preview: { title: "Quality Report", subtitle: "Automated quality scores and recommendations for the generated deck." },
  export: { title: "Export Center", subtitle: "Download the PowerPoint deck and all supporting artifacts." },
};

export function App() {
  const [activeScreen, setActiveScreen] = useState<Screen>("new");
  const [jobId, setJobId] = useState<string | null>(null);

  const { title, subtitle } = PAGE_META[activeScreen];

  return (
    <>
      {/* Sidebar navigation */}
      <ScreenTabs
        active={activeScreen}
        onChange={setActiveScreen}
        hasJob={jobId !== null}
      />

      {/* Main content area */}
      <main className="main-content">
        <header className="page-header">
          <div>
            <h1 className="page-title">{title}</h1>
            <p className="page-subtitle">{subtitle}</p>
          </div>

          {/* Job ID chip */}
          {jobId && (
            <div className="job-banner" style={{ marginBottom: 0, alignSelf: "flex-start" }}>
              <span>Job:</span>
              <code>{jobId}</code>
            </div>
          )}
        </header>

        <div className="page-body">
          {/* Active screen content */}
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
        </div>
      </main>

      {/* Global toast notifications */}
      <ToastContainer />
    </>
  );
}
