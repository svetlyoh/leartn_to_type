import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import "fake-indexeddb/auto";
import { TrainingScreen } from "./TrainingScreen";

const response = (data: unknown) => Promise.resolve({ ok: true, json: () => Promise.resolve(data) } as Response);
beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("matchMedia", () => ({ matches: false }));
  vi.stubGlobal("fetch", vi.fn((input: string) => {
    const url = String(input);
    if (url.includes("module-progress")) return response({ stage_id: "module_01", title: "Anchor Keys", progress_percent: 10, criteria: { completed_drills: { value: 0, target: 4 }, accuracy: { value: 0, target: .9 }, introduced_key_mastery: [], hint_rate: { value: 0, max: .15 } } });
    if (url.includes("progress-dashboard")) return response({ resume: {}, progress_updated_at: null });
    return response({});
  }));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("renders an 80-character drill in stable, wrap-safe standard layout", async () => {
  const text = "steady fingers follow each calm word while the prompt wraps safely inside its card.";
  const { container } = render(<TrainingScreen profileId={crypto.randomUUID()} initialPractice={{ text, description: "test", focusKeys: [], diagnostic: false }} soundEnabled={false} onExit={() => {}} onClosed={() => {}} />);
  await screen.findByText("Anchor Keys");
  const prompt = container.querySelector('.prompt[data-layout="standard"]')!;
  expect(prompt).toBeTruthy();
  expect(prompt.getAttribute("aria-label")).toBe(text);
  expect([...prompt.querySelectorAll("[data-character]")].map(node => node.getAttribute("data-character")).join("")).toBe(text);
  expect(prompt.querySelectorAll("[data-character]").length).toBe(text.length);
  expect(prompt.querySelectorAll(".space").length).toBe(text.split(" ").length - 1);
  fireEvent.keyDown(window, { key: "s", code: "KeyS" });
  expect(prompt.querySelectorAll("[data-character]").length).toBe(text.length);
  expect(prompt.querySelector(".current")).toBeTruthy();
  expect(container.querySelector(".prompt")!.compareDocumentPosition(container.querySelector(".physical-keyboard")!) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});

it("toggles hands with Space + { without changing lesson position or metrics", async () => {
  const { container } = render(<TrainingScreen profileId={crypto.randomUUID()} soundEnabled={false} onExit={() => {}} onClosed={() => {}} />);
  await screen.findByText("Anchor Keys");
  const before = screen.getByText(/Round progress/).textContent;
  fireEvent.keyDown(window, { key: " ", code: "Space" });
  fireEvent.keyDown(window, { key: "{", code: "BracketLeft", shiftKey: true });
  expect(screen.getByText(/Round progress/).textContent).toBe(before);
  expect(container.querySelectorAll("[data-hand]").length).toBe(0);
  expect(screen.getByRole("button", { name: "Show hands" }).getAttribute("aria-keyshortcuts")).toBe("Space+{");
});
