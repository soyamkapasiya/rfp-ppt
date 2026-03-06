// ─── Toast context & hook ─────────────────────────────────────────────────────
import React, {
    createContext,
    useCallback,
    useContext,
    useId,
    useReducer,
    type ReactNode,
} from "react";

export type ToastVariant = "success" | "error" | "info";

export type Toast = {
    id: string;
    variant: ToastVariant;
    title: string;
    message?: string;
};

type State = Toast[];
type Action =
    | { type: "ADD"; toast: Toast }
    | { type: "REMOVE"; id: string };

function reducer(state: State, action: Action): State {
    switch (action.type) {
        case "ADD":
            return [...state, action.toast];
        case "REMOVE":
            return state.filter((t) => t.id !== action.id);
        default:
            return state;
    }
}

type ToastContextValue = {
    toasts: Toast[];
    toast: (variant: ToastVariant, title: string, message?: string) => void;
    dismiss: (id: string) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, dispatch] = useReducer(reducer, []);

    const dismiss = useCallback((id: string) => {
        dispatch({ type: "REMOVE", id });
    }, []);

    const toast = useCallback(
        (variant: ToastVariant, title: string, message?: string) => {
            const id = crypto.randomUUID();
            dispatch({ type: "ADD", toast: { id, variant, title, message } });
            setTimeout(() => dispatch({ type: "REMOVE", id }), 5000);
        },
        []
    );

    return (
        <ToastContext.Provider value={{ toasts, toast, dismiss }}>
            {children}
        </ToastContext.Provider>
    );
}

export function useToast() {
    const ctx = useContext(ToastContext);
    if (!ctx) throw new Error("useToast must be used within ToastProvider");
    return ctx;
}

// ─── Toast UI ─────────────────────────────────────────────────────────────────
const ICONS: Record<ToastVariant, string> = {
    success: "✅",
    error: "❌",
    info: "ℹ️",
};

export function ToastContainer() {
    const { toasts, dismiss } = useToast();
    return (
        <div className="toast-container" role="region" aria-label="Notifications">
            {toasts.map((t) => (
                <div
                    key={t.id}
                    className={`toast toast-${t.variant}`}
                    role="alert"
                    onClick={() => dismiss(t.id)}
                    style={{ cursor: "pointer" }}
                >
                    <span className="toast-icon">{ICONS[t.variant]}</span>
                    <div className="toast-body">
                        <div className="toast-title">{t.title}</div>
                        {t.message && <div className="toast-msg">{t.message}</div>}
                    </div>
                </div>
            ))}
        </div>
    );
}
