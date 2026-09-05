import { useEffect, useState } from "react";
import { api } from "../api/client";
import { CHARACTERS } from "../components/characters/characterCatalog";
import {
  applyPreferences,
  loadPreferences,
  type Preferences,
  type ThemeId,
} from "../preferences";
export type PlayerProfile = {
  id: string;
  display_name: string;
  character_id: string;
  school_status: string | null;
  grade_level: string | null;
  theme_id: ThemeId;
  sound_enabled: boolean;
};
export type PreparedPractice = {
  text: string;
  description: string;
  focusKeys: string[];
  diagnostic: boolean;
};
type Dashboard = {
  curriculum: {
    phase: string;
    module_index: number;
    module_count: number;
    module_title: string;
    mastery_percent: number;
  };
  recent: {
    last: {
      net_wpm: number;
      accuracy: number;
      cadence_score: number | null;
    } | null;
    average_wpm: number | null;
    average_accuracy: number | null;
    best_wpm: number | null;
    completed_sessions: number;
    practice_ms: number;
  };
  weak_keys: string[];
  strong_keys: string[];
  history: {
    started_at: string;
    stage_id: string;
    net_wpm: number;
    accuracy: number;
    cadence_score: number | null;
  }[];
  resume: { round_index?: number; char_index?: number };
};
type WeakPractice = {
  diagnostic: boolean;
  focus_keys: string[];
  text: string;
  description: string;
};
export function PlayerMenuScreen({
  profile,
  onProfileChanged,
  onTrain,
  onHow,
  onAccessibility,
  onSwitch,
}: {
  profile: PlayerProfile;
  onProfileChanged: () => void;
  onTrain: (practice?: PreparedPractice) => void;
  onHow: () => void;
  onAccessibility: () => void;
  onSwitch: () => void;
}) {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [panel, setPanel] = useState<
    "character" | "name" | "progress" | "settings" | "weak" | null
  >(null);
  const [draftName, setDraftName] = useState(profile.display_name);
  const [prefs, setPrefs] = useState<Preferences>(() => ({
    ...loadPreferences(),
    theme_id: profile.theme_id ?? "midnight",
    sound_enabled: profile.sound_enabled ?? true,
  }));
  const [weak, setWeak] = useState<WeakPractice | null>(null);
  const [error, setError] = useState("");
  const refresh = () =>
    api<Dashboard>("/progress-dashboard")
      .then(setDashboard)
      .catch(() =>
        setError(
          "Progress is temporarily unavailable. Your training remains safe.",
        ),
      );
  useEffect(() => {
    void refresh();
    applyPreferences(prefs);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  const choose = async (id: string) => {
    await api("/profile/character", {
      method: "PATCH",
      body: JSON.stringify({ character_id: id }),
    });
    setPanel(null);
    onProfileChanged();
  };
  const saveName = async (e: React.FormEvent) => {
    e.preventDefault();
    await api("/auth/name", {
      method: "POST",
      body: JSON.stringify({ name: draftName }),
    });
    setPanel(null);
    onProfileChanged();
  };
  const savePrefs = async (next: Preferences) => {
    setPrefs(next);
    applyPreferences(next);
    try {
      await api("/settings", { method: "PATCH", body: JSON.stringify(next) });
    } catch {
      setError("Saved on this device. Server sync will be retried next time.");
    }
  };
  const prepareWeak = async () => {
    setPanel("weak");
    setWeak(null);
    setError("");
    try {
      setWeak(await api<WeakPractice>("/weak-key-practice"));
    } catch {
      setError(
        "Could not prepare weak-key practice. Continue training is still available.",
      );
    }
  };
  const character =
    CHARACTERS.find((item) => item.id === profile.character_id) ??
    CHARACTERS[0];
  const student = profile.school_status === "student" && profile.grade_level;
  return (
    <main className="menu-screen player-menu">
      <section className="hero-menu">
        <div className="player-heading">
          <img src={character.image} alt="" />
          <div>
            <p className="eyebrow">Player ready</p>
            <h1>{profile.display_name}</h1>
            {student && <p>Student · Grade {profile.grade_level}</p>}
            <p>
              {character.name} · {character.trait}
            </p>
            <button
              className="quiet"
              onClick={() => {
                setDraftName(profile.display_name);
                setPanel("name");
              }}
            >
              Edit name
            </button>
          </div>
        </div>
        <div className="status-panel">
          <span>
            Training level{" "}
            <b>
              {dashboard
                ? `${dashboard.curriculum.phase} · Module ${dashboard.curriculum.module_index} / 64`
                : "Loading…"}
            </b>
          </span>
          <span>
            Module mastery{" "}
            <b>
              {dashboard ? `${dashboard.curriculum.mastery_percent}%` : "—"}
            </b>
          </span>
          <span>
            Next focus{" "}
            <b>
              {dashboard?.weak_keys.map((k) => k.toUpperCase()).join(" / ") ||
                "Steady rhythm"}
            </b>
          </span>
          {dashboard?.resume?.char_index ? (
            <span>
              Resume{" "}
              <b>
                Round {dashboard.resume.round_index} ·{" "}
                {dashboard.resume.char_index} characters complete
              </b>
            </span>
          ) : null}
        </div>
        <nav className="menu-actions" aria-label="Player menu">
          <button onClick={() => onTrain()}>Start / Continue</button>
          <button onClick={() => void prepareWeak()}>Practice weak keys</button>
          <button className="quiet" onClick={() => setPanel("progress")}>
            Progress
          </button>
          <button className="quiet" onClick={() => setPanel("settings")}>
            Settings
          </button>
          <button className="quiet" onClick={() => setPanel("character")}>
            Select character
          </button>
          <button className="quiet" onClick={onHow}>
            How training works
          </button>
          <button className="quiet" onClick={onAccessibility}>
            Accessibility
          </button>
          <button className="quiet" onClick={onSwitch}>
            Exit
          </button>
        </nav>
        {error && (
          <p role="alert" className="warning">
            {error}
          </p>
        )}
      </section>
      {panel === "character" && (
        <Modal title="Choose your character" close={() => setPanel(null)}>
          <div className="character-picker">
            {CHARACTERS.map((item) => (
              <button
                className="tooltip-card"
                key={item.id}
                onClick={() => void choose(item.id)}
                aria-describedby={`menu-help-${item.id}`}
                aria-pressed={item.id === profile.character_id}
              >
                <img src={item.image} alt="" />
                <span>
                  {item.name} · {item.trait}
                </span>
                <span
                  role="tooltip"
                  className="character-help"
                  id={`menu-help-${item.id}`}
                >
                  {item.help}
                </span>
              </button>
            ))}
          </div>
        </Modal>
      )}
      {panel === "name" && (
        <div
          className="modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-name"
        >
          <form onSubmit={(e) => void saveName(e)}>
            <h2 id="edit-name">Edit player name</h2>
            <input
              autoFocus
              value={draftName}
              maxLength={40}
              placeholder="MCP"
              onChange={(e) => setDraftName(e.target.value)}
            />
            <button>Save name</button>
            <button
              type="button"
              className="quiet"
              onClick={() => setPanel(null)}
            >
              Cancel
            </button>
          </form>
        </div>
      )}
      {panel === "progress" && (
        <Modal title="Progress" close={() => setPanel(null)}>
          {dashboard ? (
            <div className="progress-grid">
              <article>
                <h3>Current position</h3>
                <p>{dashboard.curriculum.phase}</p>
                <p>
                  Module {dashboard.curriculum.module_index} of{" "}
                  {dashboard.curriculum.module_count} ·{" "}
                  {dashboard.curriculum.module_title}
                </p>
                <p>{dashboard.curriculum.mastery_percent}% mastery</p>
              </article>
              <article>
                <h3>Recent performance</h3>
                <p>
                  Last WPM ·{" "}
                  {dashboard.recent.last?.net_wpm?.toFixed(1) ?? "collecting"}
                </p>
                <p>
                  Accuracy ·{" "}
                  {dashboard.recent.last
                    ? `${dashboard.recent.last.accuracy.toFixed(1)}%`
                    : "collecting"}
                </p>
                <p>
                  Cadence ·{" "}
                  {dashboard.recent.last?.cadence_score?.toFixed(0) ??
                    "collecting"}
                </p>
                <p>
                  Recent average ·{" "}
                  {dashboard.recent.average_wpm?.toFixed(1) ?? "collecting"} WPM
                </p>
                <p>
                  Best valid ·{" "}
                  {dashboard.recent.best_wpm?.toFixed(1) ?? "collecting"} WPM
                </p>
                <p>{dashboard.recent.completed_sessions} completed sessions</p>
              </article>
              <article>
                <h3>Key development</h3>
                <p>
                  Weak ·{" "}
                  {dashboard.weak_keys.join(", ").toUpperCase() || "collecting"}
                </p>
                <p>
                  Stable ·{" "}
                  {dashboard.strong_keys.join(", ").toUpperCase() ||
                    "collecting"}
                </p>
              </article>
              <article>
                <h3>Recent history</h3>
                {dashboard.history.length ? (
                  <ol className="history-list">
                    {dashboard.history.slice(0, 7).map((item, index) => (
                      <li key={`${item.started_at}-${index}`}>
                        {item.stage_id} · {item.net_wpm.toFixed(0)} WPM ·{" "}
                        {item.accuracy.toFixed(0)}% ·{" "}
                        {item.cadence_score?.toFixed(0) ?? "collecting"}
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p>Complete a round to begin your history.</p>
                )}
              </article>
            </div>
          ) : (
            <p aria-busy="true">Loading progress…</p>
          )}
        </Modal>
      )}
      {panel === "settings" && (
        <Modal title="Settings" close={() => setPanel(null)}>
          <div className="settings-grid">
            <label>
              Theme
              <select
                value={prefs.theme_id}
                onChange={(e) =>
                  void savePrefs({
                    ...prefs,
                    theme_id: e.target.value as ThemeId,
                  })
                }
              >
                <option value="midnight">Midnight</option>
                <option value="soft-slate">Soft Slate</option>
                <option value="soft-plum">Soft Plum</option>
              </select>
            </label>
            <label>
              <input
                type="checkbox"
                checked={prefs.sound_enabled}
                onChange={(e) =>
                  void savePrefs({ ...prefs, sound_enabled: e.target.checked })
                }
              />{" "}
              Typing sounds
            </label>
            <label>
              <input
                type="checkbox"
                checked={prefs.reduce_motion}
                onChange={(e) =>
                  void savePrefs({ ...prefs, reduce_motion: e.target.checked })
                }
              />{" "}
              Reduce motion
            </label>
            <label>
              <input
                type="checkbox"
                checked={prefs.hand_guidance_enabled}
                onChange={(e) =>
                  void savePrefs({
                    ...prefs,
                    hand_guidance_enabled: e.target.checked,
                  })
                }
              />{" "}
              Hand guidance
            </label>
          </div>
        </Modal>
      )}
      {panel === "weak" && (
        <Modal title="Practice weak keys" close={() => setPanel(null)}>
          {weak ? (
            <>
              <p>{weak.description}</p>
              <p>
                {weak.focus_keys.length
                  ? `Focus: ${weak.focus_keys.join(", ").toUpperCase()}`
                  : "Balanced current-module diagnostic"}
              </p>
              <button
                onClick={() =>
                  onTrain({
                    text: weak.text,
                    description: weak.description,
                    focusKeys: weak.focus_keys,
                    diagnostic: weak.diagnostic,
                  })
                }
              >
                {weak.diagnostic ? "Start diagnostic" : "Start practice"}
              </button>
            </>
          ) : (
            <p aria-busy="true">Preparing a useful round…</p>
          )}
        </Modal>
      )}
    </main>
  );
}
function Modal({
  title,
  close,
  children,
}: {
  title: string;
  close: () => void;
  children: React.ReactNode;
}) {
  const id = `modal-${title.replace(/\s/g, "-")}`;
  return (
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby={id}>
      <div>
        <h2 id={id}>{title}</h2>
        {children}
        <button className="quiet" onClick={close}>
          Back
        </button>
      </div>
    </div>
  );
}
