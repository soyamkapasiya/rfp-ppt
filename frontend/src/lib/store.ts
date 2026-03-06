export type Screen = "new" | "console" | "questions" | "preview" | "export";

export type LocalStore = {
  activeScreen: Screen;
  jobId: string | null;
};

export const initialStore: LocalStore = {
  activeScreen: "new",
  jobId: null,
};
