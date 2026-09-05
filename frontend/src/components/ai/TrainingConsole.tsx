import { useEffect, useRef, useState } from "react";
import { api } from "../../api/client";
import { TRAINING_SHORTCUTS } from "../../config/shortcuts";
type Action = {
  id: string;
  label: string;
  enabled: boolean;
  reason?: string | null;
};
type Options = {
  capability_band: string;
  actions: Action[];
  passage_options: {
    durations_seconds: number[];
    topic_passages: boolean;
    long_form: boolean;
    numbers: boolean;
    symbols: boolean;
  };
};
type Status = {
  state: "ready" | "builtin" | "connecting";
  lesson_generation_available: boolean;
};
export function TrainingConsole({
  open,
  onToggle,
  onAction,
  onShowHands,
  moduleTitle,
  modulePercent,
}: {
  open: boolean;
  onToggle: () => void;
  onShowHands?: () => void;
  onAction: (action: string, request?: string) => Promise<boolean>;
  moduleTitle: string;
  modulePercent: number;
}) {
  const first = useRef<HTMLButtonElement>(null);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<Status | null>(null);
  const [options, setOptions] = useState<Options | null>(null);
  const [building, setBuilding] = useState(false);
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (!open) return;
    first.current?.focus();
    Promise.all([api<Status>("/ai/status"), api<Options>("/training/options")])
      .then(([s, o]) => {
        setStatus(s);
        setOptions(o);
      })
      .catch(() =>
        setStatus({ state: "builtin", lesson_generation_available: false }),
      );
  }, [open]);
  const submit = async (action: string, request?: string) => {
    if (building) return;
    setBuilding(true);
    setMessage("Building practice…");
    const ok = await onAction(action, request);
    setBuilding(false);
    setMessage(
      ok
        ? "Ready. Review the practice preview and choose your next action."
        : "I could not build that practice. Try another request or keep the current round.",
    );
  };
  if (!open)
    return (
      <aside className="console collapsed">
        <p className="eyebrow">
          AI: {status?.state === "builtin" ? "Built-in mode" : "Ready"}
        </p>
        <button
          title={`Open Training Console (${TRAINING_SHORTCUTS.toggleAI})`}
          aria-keyshortcuts="F1"
          onClick={onToggle}
        >
          Open Training Console <kbd>F1</kbd>
        </button>
      </aside>
    );
  const actions = options?.actions ?? [
    { id: "continue", label: "Continue the plan", enabled: true },
    { id: "reshuffle", label: "Give me another short pattern", enabled: true },
  ];
  return (
    <aside className="console expanded" aria-label="Training Console">
      <div className="console-head">
        <div>
          <p className="eyebrow">
            Training console ·{" "}
            {status?.state === "builtin" ? "built-in mode" : "AI ready"}
          </p>
          <h2>
            {moduleTitle} · {modulePercent}% mastery
          </h2>
        </div>
        <button
          title={`Back to training (${TRAINING_SHORTCUTS.returnToTraining})`}
          aria-keyshortcuts="Escape"
          onClick={onToggle}
        >
          Back to training <kbd>Esc</kbd>
        </button>
      </div>
      <p>You’re building this module one clean pattern at a time.</p>
      {status?.state === "builtin" && (
        <p className="notice">
          AI is unavailable right now. Built-in training is ready.
        </p>
      )}
      <div className="console-options">
        {actions.slice(0, 4).map((action, index) => (
          <button
            key={action.id}
            ref={index === 0 ? first : undefined}
            disabled={!action.enabled || building}
            title={action.reason ?? action.label}
            aria-keyshortcuts={action.id === "reshuffle" ? "F2" : undefined}
            onClick={() => void submit(action.id)}
          >
            {action.label}
            {action.id === "reshuffle" && <kbd>F2</kbd>}
            {!action.enabled && action.reason && <small>{action.reason}</small>}
          </button>
        ))}
      </div>
      {options && !options.passage_options.topic_passages && <div className="notice">
        <p>Full sentences unlock after you learn more letters. I can build a fresh pattern with the keys you know now.</p>
        <button disabled={building} onClick={() => void submit("reshuffle")}>Build short pattern</button>
        {onShowHands && <button onClick={onShowHands}>Show finger placement</button>}
        <button onClick={onToggle}>Keep current round</button>
      </div>}
      <form
        className="ai-input"
        onSubmit={(event) => {
          event.preventDefault();
          const value = input.trim();
          if (value) void submit("custom_passage", value);
        }}
      >
        <label>
          Something else…
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Give me something about running"
          />
        </label>
        <button type="submit" disabled={!input.trim() || building}>
          {building ? "Building practice…" : "Build practice"}
        </button>
      </form>
      {message && (
        <p
          role="status"
          className={message.startsWith("I could") ? "warning" : "notice"}
        >
          {message}
        </p>
      )}
    </aside>
  );
}
