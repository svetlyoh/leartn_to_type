import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createState, applyInput, pause, resume } from "../typing-core/engine";
import type { TypingState } from "../typing-core/types";
import {
  accuracy,
  cadenceCv,
  cadenceScore,
  grossWpm,
} from "../typing-core/metrics";
import { VisualKeyboard } from "../components/training/VisualKeyboard";
import { HandsOverlay } from "../components/training/HandsOverlay";
import { placementSignature } from "../components/training/keyboardGeometry";
import { HandGuide } from "../components/training/HandGuide";
import { TrainingConsole } from "../components/ai/TrainingConsole";
import { coachNote, type CoachMode } from "../components/coach/coachRules";
import { CURRICULUM } from "../generated/curriculum.generated";
import {
  ModuleProgress,
  type ModuleProgressData,
} from "../components/training/ModuleProgress";
import { SessionControls } from "../components/training/SessionControls";
import {
  loadActive,
  saveActive,
  type SavedSession,
} from "../persistence/activeSessionStore";
import { api } from "../api/client";
import { useTrainingShortcuts } from "../hooks/useTrainingShortcuts";
import { TRAINING_SHORTCUTS } from "../config/shortcuts";
import type { PreparedPractice } from "./PlayerMenuScreen";
import { loadPreferences } from "../preferences";
import { playTypingSound } from "../typingSound";
import { getPromptLayoutMode } from "../components/training/promptLayout";

type LessonSource = SavedSession["source"];
type GeneratedLesson = {
  lesson_id: string;
  text: string;
  lesson_kind: "drill" | "passage";
  source: "ai" | "cache" | "fallback";
  estimated_duration_seconds: number | null;
};
type ServerResume = {
  resume: {
    lesson_id?: string;
    lesson_index?: number;
    stage_id?: string;
    char_index?: number;
    elapsed_active_ms?: number;
    prompt?: string;
    source?: LessonSource;
  };
  progress_updated_at: string | null;
};

export function TrainingScreen({
  profileId,
  initialPractice,
  soundEnabled,
  onExit,
  onClosed,
}: {
  profileId: string;
  initialPractice?: PreparedPractice;
  soundEnabled: boolean;
  onExit: () => void;
  onClosed: () => void;
}) {
  const lessons = CURRICULUM.lessons;
  const [lessonIndex, setLessonIndex] = useState(0);
  const authored = lessons[lessonIndex];
  const [lessonId, setLessonId] = useState<string>(
    initialPractice ? "prepared-practice" : authored.id,
  );
  const [stageId, setStageId] = useState<string>(authored.stageId);
  const [source, setSource] = useState<LessonSource>(
    initialPractice ? "fallback" : "authored",
  );
  const [state, setState] = useState<TypingState>(() =>
    createState(initialPractice?.text ?? authored.text),
  );
  const [mode, setMode] = useState<CoachMode>("calm");
  const [hideMetrics, setHideMetrics] = useState(false);
  const [consoleOpen, setConsoleOpen] = useState(false);
  const [saveStatus, setSaveStatus] = useState(
    initialPractice?.description ?? "",
  );
  const [exitOpen, setExitOpen] = useState(false);
  const [reshuffleOpen, setReshuffleOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pending, setPending] = useState<GeneratedLesson | null>(null);
  const [lessonKind, setLessonKind] = useState<string | undefined>(initialPractice ? "drill" : undefined);
  const [estimatedDurationSeconds, setEstimatedDurationSeconds] = useState<number | null>(null);
  const [suspended, setSuspended] = useState<SavedSession | null>(null);
  useEffect(() => { void loadActive(`${profileId}:suspended`).then(value => setSuspended(value ?? null)); }, [profileId]);
  const [moduleProgress, setModuleProgress] =
    useState<ModuleProgressData | null>(null);
  const [hiddenPlacement, setHiddenPlacement] = useState<string | null>(null);
  const stage = CURRICULUM.stages.find(item => item.id === stageId) ?? CURRICULUM.stages[0];
  const placement = placementSignature(stageId, [...new Set(state.prompt)], stage.introducedKeys);
  const guideVisible = hiddenPlacement !== placement;
  const setGuideVisible = (visible: boolean) => setHiddenPlacement(visible ? null : placement);
  useEffect(() => setHiddenPlacement(null), [placement]);
  const surface = useRef<HTMLElement>(null);
  const activeCharacter = useRef<HTMLSpanElement>(null);
  const hydrated = useRef(false);
  const completedSync = useRef<string | null>(null);
  const recentPractice = useRef<string[]>([]);
  const preferences = loadPreferences();
  const reduceMotion =
    preferences.reduce_motion ||
    matchMedia("(prefers-reduced-motion: reduce)").matches;
  const promptLayout = getPromptLayoutMode(state.prompt.length, lessonKind, estimatedDurationSeconds);
  const passageMode = promptLayout === "passage";
  const stateRef = useRef(state);
  stateRef.current = state;
  const spaceSnapshot = useRef<TypingState | null>(null);

  useEffect(() => {
    if (initialPractice) {
      api<ModuleProgressData>("/module-progress")
        .then(setModuleProgress)
        .catch(() => setSaveStatus("Local training is ready"))
        .finally(() => {
          hydrated.current = true;
          setTimeout(() => surface.current?.focus(), 0);
        });
      return;
    }
    Promise.all([
      loadActive(profileId),
      api<ModuleProgressData>("/module-progress"),
      api<ServerResume>("/progress-dashboard"),
    ])
      .then(([saved, progress, server]) => {
        const serverIsNewer = Boolean(
          server.progress_updated_at &&
            (!saved ||
              new Date(server.progress_updated_at).getTime() >
                new Date(saved.updatedAt).getTime()),
        );
        if (serverIsNewer && server.resume?.prompt) {
          const resume = server.resume;
          const restored = createState(resume.prompt!);
          restored.position = Math.min(
            Number(resume.char_index ?? 0),
            restored.prompt.length,
          );
          restored.correctChars = restored.position;
          restored.attempts = restored.position;
          restored.activeMs = Number(resume.elapsed_active_ms ?? 0);
          setLessonIndex(
            Math.min(Number(resume.lesson_index ?? 0), lessons.length - 1),
          );
          setLessonId(resume.lesson_id ?? lessons[0].id);
          setStageId(resume.stage_id ?? progress.stage_id);
          setSource(resume.source ?? "authored");
          setState(restored);
          setSaveStatus("Latest server checkpoint restored");
        } else if (saved?.saveVersion === 1) {
          const current = performance.now();
          setLessonIndex(Math.min(saved.lessonIndex, lessons.length - 1));
          setLessonId(saved.lessonId);
          setStageId(saved.stageId);
          setSource(saved.source);
          setState({
            ...saved.typingState,
            startedAt:
              saved.typingState.startedAt === null
                ? null
                : current - saved.typingState.activeMs,
            lastCorrectAt: null,
            pausedAt: null,
          });
          setSaveStatus(
            saved.pendingSync
              ? "Saved on this device · sync pending"
              : "Saved session restored",
          );
        } else {
          const index = lessons.findIndex(
            (item) => item.stageId === progress.stage_id,
          );
          if (index >= 0) {
            setLessonIndex(index);
            setLessonId(lessons[index].id);
            setStageId(lessons[index].stageId);
            setState(createState(lessons[index].text));
          }
        }
        setModuleProgress(progress);
      })
      .catch(() => setSaveStatus("Local training is ready"))
      .finally(() => {
        hydrated.current = true;
        setTimeout(() => surface.current?.focus(), 0);
      });
  }, [initialPractice, lessons, profileId]);
  useEffect(() => {
    if (passageMode && state.position > 0 && consoleOpen) setConsoleOpen(false);
  }, [consoleOpen, passageMode, state.position]);
  useEffect(() => {
    if (passageMode)
      activeCharacter.current?.scrollIntoView({
        block: "center",
        behavior: reduceMotion ? "auto" : "smooth",
      });
  }, [passageMode, reduceMotion, state.position]);
  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      if (
        e.key === "F1" ||
        e.key === "F2" ||
        e.key === "F3" ||
        (e.shiftKey && e.key === "Enter")
      )
        return;
      const target = e.target;
      if (
        target instanceof Element && target.matches('input,button,select,textarea,[contenteditable="true"]')
      )
        return;
      e.preventDefault();
      if (e.code === "Space" && !e.repeat) spaceSnapshot.current = stateRef.current;
      if (e.key.length === 1)
        playTypingSound(
          soundEnabled && loadPreferences().sound_enabled,
          e.key === " ",
        );
      setState((s) =>
        applyInput(s, {
          key: e.key,
          code: e.code,
          time: performance.now(),
          repeat: e.repeat,
          ctrlKey: e.ctrlKey,
          metaKey: e.metaKey,
          altKey: e.altKey,
        }),
      );
    };
    const blur = () => setState((s) => pause(s, performance.now()));
    const focus = () => {
      if (!consoleOpen) setState((s) => resume(s, performance.now()));
    };
    addEventListener("keydown", key);
    addEventListener("blur", blur);
    addEventListener("focus", focus);
    return () => {
      removeEventListener("keydown", key);
      removeEventListener("blur", blur);
      removeEventListener("focus", focus);
    };
  }, [consoleOpen, soundEnabled]);

  const metrics = useMemo(() => {
    const usable = state.intervals.filter(
      (value) => value > 0 && value <= 4000,
    );
    return {
      wpm: grossWpm(state.correctChars, state.activeMs),
      accuracy: accuracy(state.correctChars, state.attempts),
      cadence: usable.length >= 12 ? cadenceScore(usable) : null,
    };
  }, [state]);
  const makeSaved = useCallback(
    (pendingSync: boolean, checkpointId: string): SavedSession => ({
      id: profileId,
      saveVersion: 1,
      lessonId,
      lessonIndex,
      stageId,
      typingState: pause(state, performance.now()),
      source,
      updatedAt: new Date().toISOString(),
      pendingSync,
      localCheckpointId: checkpointId,
    }),
    [lessonId, lessonIndex, profileId, source, stageId, state],
  );
  const checkpoint = useCallback(async () => {
    setState((current) => pause(current, performance.now()));
    const checkpointId = `chk_${crypto.randomUUID()}`;
    const saved = makeSaved(true, checkpointId);
    await saveActive(saved);
    const payload = {
      save_version: 1,
      curriculum_version: CURRICULUM.version,
      stage_id: stageId,
      lesson_id: lessonId,
      char_index: state.position,
      round_index: lessonIndex + 1,
      lesson_index: lessonIndex,
      elapsed_active_ms: state.activeMs,
      prompt: state.prompt,
      source,
      difficulty: "practice",
      weak_keys: [],
      local_checkpoint_id: checkpointId,
    };
    try {
      await api("/session-checkpoint", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      await saveActive({ ...saved, pendingSync: false });
      setSaveStatus("Saved");
    } catch {
      setSaveStatus("Saved on this device · sync pending");
    }
  }, [
    lessonId,
    lessonIndex,
    makeSaved,
    source,
    stageId,
    state.activeMs,
    state.position,
    state.prompt,
  ]);
  useEffect(() => {
    if (!hydrated.current) return;
    const timer = setInterval(() => void checkpoint(), 45000);
    return () => clearInterval(timer);
  }, [checkpoint]);
  useEffect(() => {
    if (!hydrated.current || !moduleProgress || moduleProgress.stage_id === stageId) return;
    void checkpoint().then(() => api<ModuleProgressData>('/module-progress')).then(setModuleProgress)
      .catch(() => setSaveStatus('Module sync pending. Your round is saved on this device.'));
  }, [stageId, moduleProgress?.stage_id, checkpoint]);
  useEffect(() => {
    if (state.complete && hydrated.current) void checkpoint();
  }, [checkpoint, state.complete]);
  useEffect(() => {
    if (
      !state.complete ||
      !hydrated.current ||
      completedSync.current === lessonId
    )
      return;
    completedSync.current = lessonId;
    const usable = state.intervals.filter(
      (value) => value > 0 && value <= 4000,
    );
    const syncId = `round_${crypto.randomUUID()}`;
    void api("/training-sessions", {
      method: "POST",
      body: JSON.stringify({
        sync_id: syncId,
        lesson_id: lessonId,
        stage_id: stageId,
        started_at: new Date(Date.now() - state.activeMs).toISOString(),
        duration_ms: state.activeMs,
        active_duration_ms: state.activeMs,
        char_attempts: state.attempts,
        correct_chars: state.correctChars,
        error_count: state.errors,
        gross_wpm: metrics.wpm,
        net_wpm: metrics.wpm,
        accuracy: metrics.accuracy,
        cadence_score: metrics.cadence,
        cadence_cv: cadenceCv(usable),
        stall_count: state.stalls,
        key_stats: state.keyStats,
        source,
      }),
    })
      .then(() =>
        api<ModuleProgressData>("/module-progress").then(setModuleProgress),
      )
      .catch(() => setSaveStatus("Round complete · server sync pending"));
  }, [lessonId, metrics, state, stageId, source]);
  useEffect(() => {
    const hidden = () => {
      if (document.visibilityState === "hidden") void checkpoint();
    };
    const pagehide = () => {
      const checkpointId = `chk_${crypto.randomUUID()}`;
      void saveActive(makeSaved(true, checkpointId));
    };
    document.addEventListener("visibilitychange", hidden);
    addEventListener("pagehide", pagehide);
    return () => {
      document.removeEventListener("visibilitychange", hidden);
      removeEventListener("pagehide", pagehide);
    };
  }, [checkpoint, makeSaved]);

  const next = useCallback(() => {
    if (loading) return;
    const index = (lessonIndex + 1) % lessons.length;
    setLessonIndex(index);
    setLessonId(lessons[index].id);
    setStageId(lessons[index].stageId);
    setSource("authored");
    setLessonKind(undefined);
    setEstimatedDurationSeconds(null);
    setState(createState(lessons[index].text));
    completedSync.current = null;
    setPending(null);
    setSaveStatus("");
    setTimeout(() => surface.current?.focus(), 0);
  }, [lessonIndex, lessons, loading]);
  const requestLesson = useCallback(
    async (action = "reshuffle", request = ""): Promise<boolean> => {
      if (action === "continue") {
        setConsoleOpen(false);
        setTimeout(() => surface.current?.focus(), 0);
        return true;
      }
      if (loading) return false;
      setLoading(true);
      try {
        if (moduleProgress?.stage_id !== stageId) {
          await checkpoint();
          setModuleProgress(await api<ModuleProgressData>('/module-progress'));
        }
        const topic = request.toLowerCase().includes("running")
          ? "running"
          : request.slice(0, 60);
        const durationMatch = request.match(/(one|1)[ -]?minute/i);
        const target =
          action === "custom_passage"
            ? Math.max(80, state.prompt.length)
            : Math.max(20, Math.min(state.prompt.length, 160));
        const generated = await api<GeneratedLesson>("/ai/lesson", {
          method: "POST",
          body: JSON.stringify({
            request_id: crypto.randomUUID(),
            recent_texts: [state.prompt, ...recentPractice.current],
            schema_version: 1,
            curriculum_version: CURRICULUM.version,
            stage_id: stageId,
            mode: action,
            difficulty: "practice",
            target_characters: target,
            target_duration_seconds: durationMatch ? 60 : undefined,
            topic,
          }),
        });
        if (!generated.text || [...generated.text].some(key => !stage.allowedCharacters.includes(key))) throw new Error("Practice contains keys outside this module");
        recentPractice.current = [generated.text, ...recentPractice.current].slice(0, 6);
        setPending(generated);
        setSaveStatus(
          generated.source === "fallback"
            ? "Built-in practice prepared"
            : "New practice prepared",
        );
        return true;
      } catch (error) {
        setSaveStatus(`Practice could not be built. ${error instanceof Error ? error.message : 'Connection unavailable'}. Try again or keep the current round.`);
        return false;
      } finally {
        setLoading(false);
        setConsoleOpen(true);
      }
    },
    [loading, stageId, stage, state.prompt, pending, moduleProgress?.stage_id, checkpoint],
  );
  const startPending = async () => {
    if (!pending) return;
    if (state.position > 0 && !state.complete) {
      await checkpoint();
      const saved = {...makeSaved(true, `chk_${crypto.randomUUID()}`), id: `${profileId}:suspended`};
      try { await saveActive(saved); setSuspended(saved); }
      catch { setSaveStatus('Could not save this round. Keep it open and try again.'); return; }
    }
    setLessonId(pending.lesson_id);
    setSource(pending.source);
    setLessonKind(pending.lesson_kind);
    setEstimatedDurationSeconds(pending.estimated_duration_seconds);
    setState(createState(pending.text));
    completedSync.current = null;
    setPending(null);
    setConsoleOpen(false);
    setTimeout(() => surface.current?.focus(), 0);
  };
  const reshuffle = useCallback(() => {
    if (state.position > 0 && !state.complete) setReshuffleOpen(true);
    else void requestLesson("reshuffle");
  }, [requestLesson, state.complete, state.position]);
  const toggleConsole = useCallback(() => {
    setConsoleOpen((value) => {
      const nextOpen = !value;
      setState((current) =>
        nextOpen
          ? pause(current, performance.now())
          : resume(current, performance.now()),
      );
      if (!nextOpen) setTimeout(() => surface.current?.focus(), 0);
      return nextOpen;
    });
  }, []);
  const back = useCallback(() => {
    setConsoleOpen(false);
    setState((current) => resume(current, performance.now()));
    setTimeout(() => surface.current?.focus(), 0);
  }, []);
  useTrainingShortcuts({
    canNext: state.complete && !loading,
    consoleOpen,
    onNext: next,
    onToggleConsole: toggleConsole,
    onReshuffle: reshuffle,
    onReturn: back,
    onToggleHands: () => setGuideVisible(!guideVisible),
    onHandsChord: () => {
      if (spaceSnapshot.current) setState(spaceSnapshot.current);
      spaceSnapshot.current = null;
    },
    onSpaceReleased: () => { spaceSnapshot.current = null; },
  });
  const saveExit = async () => {
    await checkpoint();
    onExit();
  };
  const close = async () => {
    await checkpoint();
    try {
      await api("/auth/profile-exit", { method: "POST", body: "{}" });
    } catch {
      /* local checkpoint is already safe */
    }
    window.close();
    onClosed();
  };

  return (
    <main
      ref={surface}
      tabIndex={-1}
      className={`${consoleOpen ? "console-mode " : ""}${passageMode ? "passage-mode" : ""}`}
    >
      <header className="topbar">
        <div>
          <span className="mark">C</span>
          <strong>Cadence</strong>
        </div>
        <SessionControls
          onSave={() => void checkpoint()}
          onExit={() => setExitOpen(true)}
          onClose={() => void close()}
          status={saveStatus}
        />
        <div className="controls">
          <label>
            Coach{" "}
            <select
              value={mode}
              onChange={(event) => setMode(event.target.value as CoachMode)}
            >
              <option value="silent">Silent</option>
              <option value="calm">Calm</option>
              <option value="competitive">Competitive</option>
            </select>
          </label>
          <label>
            <input
              type="checkbox"
              checked={hideMetrics}
              onChange={(event) => setHideMetrics(event.target.checked)}
            />{" "}
            Hide metrics
          </label>
        </div>
      </header>
      <div className="shell">
        <section className="lesson">
          <ModuleProgress data={moduleProgress} />
          <p className="eyebrow">
            Round {lessonIndex + 1} of {lessons.length} · technique first
          </p>
          <h1>{authored.title}</h1>
          <p className="instruction">
            Keep your wrists relaxed. Find the active key, then keep your eyes
            on the screen.
          </p>
          {!hideMetrics && (
            <div className="metrics">
              <span>
                <b>{state.correctChars < 10 ? "—" : metrics.wpm.toFixed(0)}</b>{" "}
                WPM
              </span>
              <span>
                <b>{state.attempts ? metrics.accuracy.toFixed(0) : "—"}</b>{" "}
                accuracy
              </span>
              <span>
                <b>{metrics.cadence?.toFixed(0) ?? "—"}</b> cadence
                <small>{metrics.cadence === null ? "collecting" : ""}</small>
              </span>
            </div>
          )}
          <div className="prompt" data-layout={promptLayout} aria-label={state.prompt}>
            <span className="sr-only">{state.prompt}</span>
            <span className="prompt-text" aria-hidden="true">
            {[...state.prompt].map((character, index) => (
              <span
                ref={index === state.position ? activeCharacter : undefined}
                key={index}
                className={`${character === " " ? "space " : ""}${
                  index < state.position
                    ? "done"
                    : index === state.position
                      ? "current"
                      : ""
                }`}
                data-character={character}
              >
                {character}
              </span>
            ))}
            </span>
          </div>
          <p className="position">
            Round progress · {state.position} / {state.prompt.length} characters
          </p>
          {suspended && <button className="quiet" onClick={async () => {
            await checkpoint();
            setLessonId(suspended.lessonId); setLessonIndex(suspended.lessonIndex);
            setStageId(suspended.stageId); setSource(suspended.source);
            setState({...suspended.typingState, pausedAt: null, lastCorrectAt: null});
            setConsoleOpen(false); setTimeout(() => surface.current?.focus(), 0);
          }}>Resume saved round</button>}
          <VisualKeyboard
            active={state.prompt[state.position]}
            error={state.lastErrorKey ?? undefined}
            allowed={[...stage.allowedCharacters]}
          >
            {guideVisible && <HandsOverlay key={lessonId} introduced={state.position === 0 ? stage.introducedKeys : []} target={state.prompt[state.position] ?? stage.introducedKeys[0] ?? "f"} reduceMotion={reduceMotion} />}
          </VisualKeyboard>
          <HandGuide
            target={state.prompt[state.position] ?? ""}
            show={guideVisible}
            reduceMotion={reduceMotion}
            onHide={() => setGuideVisible(false)}
          />
          {!guideVisible && <button className="quiet" aria-keyshortcuts="Space+Shift+{" title="Show hands · Space + Shift + {" onClick={() => setGuideVisible(true)}>Show hands <kbd aria-hidden="true">Space + Shift + {"{"}</kbd></button>}
          {state.complete && (
            <div className="complete">
              <h2>Round complete</h2>
              <p>{coachNote(mode, metrics.accuracy, metrics.wpm)}</p>
              <button
                onClick={next}
                disabled={loading}
                title={`Next training round (${TRAINING_SHORTCUTS.nextRound})`}
                aria-keyshortcuts="Shift+Enter"
              >
                Next training round <kbd>Shift + Enter</kbd>
              </button>
            </div>
          )}
        </section>
        <TrainingConsole
          open={consoleOpen}
          onToggle={toggleConsole}
          onAction={(action, request) => action === "reshuffle" ? (reshuffle(), Promise.resolve(true)) : requestLesson(action, request)}
          onShowHands={() => setGuideVisible(true)}
          moduleTitle={moduleProgress?.title ?? "Current module"}
          modulePercent={moduleProgress?.progress_percent ?? 0}
        />
      </div>
      {pending && (
        <div className="modal" role="dialog" aria-modal="true">
          <div>
            <p className="eyebrow">Validated practice ready</p>
            <h2>
              {pending.lesson_kind === "passage"
                ? "Your passage is ready"
                : "Your drill is ready"}
            </h2>
            <p>
              {pending.text.length} characters, kept inside your current key
              set. Your current round stays in place until you start.
            </p>
            <pre className="practice-preview">{pending.text}</pre>
            {stage.order <= 10 && <p>Full sentences unlock after you learn more letters. I made a new key-safe practice instead.</p>}
            <button onClick={() => void startPending()}>{state.position > 0 && !state.complete ? 'Save & start practice' : 'Start practice'}</button>
            <button onClick={() => void requestLesson("reshuffle")}>
              Reshuffle again
            </button>
            <button className="quiet" onClick={() => setPending(null)}>
              Keep current lesson
            </button>
          </div>
        </div>
      )}
      {exitOpen && (
        <div className="modal" role="dialog" aria-modal="true">
          <div>
            <h2>Exit training?</h2>
            <p>Your current round will be saved so you can resume it later.</p>
            <button onClick={() => void saveExit()}>Save &amp; Exit</button>
            <button className="quiet" onClick={() => setExitOpen(false)}>
              Keep training
            </button>
          </div>
        </div>
      )}
      {reshuffleOpen && (
        <div className="modal" role="dialog" aria-modal="true">
          <div>
            <h2>Reshuffle this round?</h2>
            <p>Your current round is not finished.</p>
            <button
              onClick={() => {
                setReshuffleOpen(false);
                void requestLesson("reshuffle");
              }}
            >
              Prepare reshuffle
            </button>
            <button className="quiet" onClick={() => setReshuffleOpen(false)}>
              Keep current
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
