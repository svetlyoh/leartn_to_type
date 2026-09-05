import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { PlayerMenuScreen, type PlayerProfile } from "./PlayerMenuScreen";
import { TrainingConsole } from "../components/ai/TrainingConsole";
import { HandGuide } from "../components/training/HandGuide";
import {
  applyPreferences,
  DEFAULT_PREFERENCES,
  loadPreferences,
} from "../preferences";

const profile: PlayerProfile = {
  id: "p1",
  display_name: "Julian",
  character_id: "runner_01",
  school_status: "student",
  grade_level: "9",
  theme_id: "midnight",
  sound_enabled: true,
};
const dashboard = {
  curriculum: {
    phase: "Foundations",
    module_index: 7,
    module_count: 64,
    module_title: "Reach",
    mastery_percent: 43,
  },
  recent: {
    last: { net_wpm: 31.2, accuracy: 96.4, cadence_score: null },
    average_wpm: 30,
    average_accuracy: 95,
    best_wpm: 38,
    completed_sessions: 4,
    practice_ms: 60000,
  },
  weak_keys: ["r", "t"],
  strong_keys: ["f", "j"],
  history: [],
  resume: { round_index: 2, char_index: 84 },
};
const response = (data: unknown) =>
  Promise.resolve({ ok: true, json: () => Promise.resolve(data) } as Response);
beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | string) => {
      const url = String(input);
      if (url.includes("progress-dashboard")) return response(dashboard);
      if (url.includes("weak-key-practice"))
        return response({
          diagnostic: false,
          focus_keys: ["r", "t"],
          text: "r t r t",
          description: "Focused practice for R, T.",
        });
      if (url.includes("ai/status"))
        return response({
          state: "builtin",
          lesson_generation_available: false,
        });
      if (url.includes("training/options"))
        return response({
          capability_band: "early",
          actions: [],
          passage_options: {
            durations_seconds: [],
            topic_passages: false,
            long_form: false,
            numbers: false,
            symbols: false,
          },
        });
      return response({ ok: true });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());
describe("REV11 player experience", () => {
  it("shows saved school detail and authoritative training level", async () => {
    render(
      <PlayerMenuScreen
        profile={profile}
        onProfileChanged={() => {}}
        onTrain={() => {}}
        onHow={() => {}}
        onAccessibility={() => {}}
        onSwitch={() => {}}
      />,
    );
    expect(screen.getByText("Student · Grade 9")).toBeTruthy();
    await screen.findByText("Foundations · Module 7 / 64");
  });
  it("opens a functional progress view and renders collecting cadence", async () => {
    render(
      <PlayerMenuScreen
        profile={profile}
        onProfileChanged={() => {}}
        onTrain={() => {}}
        onHow={() => {}}
        onAccessibility={() => {}}
        onSwitch={() => {}}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: "Progress" }));
    expect(await screen.findByText("Module 7 of 64 · Reach")).toBeTruthy();
    expect(screen.getByText("Cadence · collecting")).toBeTruthy();
  });
  it("builds server-evidenced weak-key practice and starts it", async () => {
    const start = vi.fn();
    render(
      <PlayerMenuScreen
        profile={profile}
        onProfileChanged={() => {}}
        onTrain={start}
        onHow={() => {}}
        onAccessibility={() => {}}
        onSwitch={() => {}}
      />,
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Practice weak keys" }),
    );
    expect(await screen.findByText("Focus: R, T")).toBeTruthy();
    await userEvent.click(
      screen.getByRole("button", { name: "Start practice" }),
    );
    expect(start).toHaveBeenCalledWith(
      expect.objectContaining({ focusKeys: ["r", "t"], text: "r t r t" }),
    );
  });
  it("exposes all cosmetic character explanations to keyboard users", async () => {
    render(
      <PlayerMenuScreen
        profile={profile}
        onProfileChanged={() => {}}
        onTrain={() => {}}
        onHow={() => {}}
        onAccessibility={() => {}}
        onSwitch={() => {}}
      />,
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Select character" }),
    );
    for (const text of [
      "smooth, repeatable timing",
      "resetting quickly after a mistake",
      "accurate finger placement",
      "relaxed concentration",
    ])
      expect(screen.getByText(new RegExp(text)).getAttribute("role")).toBe(
        "tooltip",
      );
  });
  it("applies and persists each semantic theme immediately", () => {
    for (const theme_id of ["midnight", "soft-slate", "soft-plum"] as const) {
      applyPreferences({ ...DEFAULT_PREFERENCES, theme_id });
      expect(document.documentElement.dataset.theme).toBe(theme_id);
      expect(loadPreferences().theme_id).toBe(theme_id);
    }
  });
});
describe("round hand guide", () => {
  it("maps R to the left index and U to the right index", () => {
    const { rerender } = render(
      <HandGuide target="r" show reduceMotion={false} onHide={() => {}} />,
    );
    expect(screen.getByText(/left index/)).toBeTruthy();
    rerender(<HandGuide target="u" show reduceMotion onHide={() => {}} />);
    expect(screen.getByText(/right index/)).toBeTruthy();
  });
  it("supports a real Hide hands control without stealing focus", async () => {
    const hide = vi.fn();
    render(<HandGuide target="w" show reduceMotion onHide={hide} />);
    await userEvent.click(screen.getByRole("button", { name: "Hide hands" }));
    expect(hide).toHaveBeenCalledOnce();
    expect(screen.getByText(/S → W → S/)).toBeTruthy();
  });
});
describe("Coach custom practice regression", () => {
  it("uses one action handler for keyboard submit and shows loading then success", async () => {
    let finish: (value: boolean) => void = () => {};
    const action = vi.fn(
      () =>
        new Promise<boolean>((resolve) => {
          finish = resolve;
        }),
    );
    render(
      <TrainingConsole
        open
        onToggle={() => {}}
        onAction={action}
        moduleTitle="Reach"
        modulePercent={43}
      />,
    );
    const input = screen.getByPlaceholderText(
      "Give me something about running",
    );
    await userEvent.type(
      input,
      "Give me something about running for one minute",
    );
    await userEvent.keyboard("{Enter}");
    expect(action).toHaveBeenCalledWith(
      "custom_passage",
      "Give me something about running for one minute",
    );
    expect(
      (
        screen.getByRole("button", {
          name: "Building practice…",
        }) as HTMLButtonElement
      ).disabled,
    ).toBe(true);
    finish(true);
    await screen.findByText(/Ready. Review the practice preview/);
  });
  it("prevents duplicate submissions while generation is in flight", async () => {
    const action = vi.fn(() => new Promise<boolean>(() => {}));
    render(
      <TrainingConsole
        open
        onToggle={() => {}}
        onAction={action}
        moduleTitle="Reach"
        modulePercent={43}
      />,
    );
    await userEvent.type(
      screen.getByPlaceholderText("Give me something about running"),
      "Give me text to type",
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Build practice" }),
    );
    await userEvent.keyboard("{Enter}");
    expect(action).toHaveBeenCalledTimes(1);
  });
  it("shows an actionable error instead of a silent no-op", async () => {
    render(
      <TrainingConsole
        open
        onToggle={() => {}}
        onAction={async () => false}
        moduleTitle="Reach"
        modulePercent={43}
      />,
    );
    await userEvent.type(
      screen.getByPlaceholderText("Give me something about running"),
      "longer paragraph",
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Build practice" }),
    );
    expect(
      await screen.findByText(/could not build that practice/i),
    ).toBeTruthy();
  });
});
