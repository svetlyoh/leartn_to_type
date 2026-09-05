import { beforeEach, describe, expect, it, vi } from "vitest";
describe("soft typing sound", () => {
  beforeEach(() => vi.resetModules());
  it("creates no audio when sound is disabled", async () => {
    const audio = vi.fn();
    vi.stubGlobal("AudioContext", audio);
    const { playTypingSound } = await import("./typingSound");
    playTypingSound(false);
    expect(audio).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });
  it("uses a short low-volume local oscillator after interaction when enabled", async () => {
    const start = vi.fn(), stop = vi.fn();
    const gain = {
      gain: { setValueAtTime: vi.fn(), exponentialRampToValueAtTime: vi.fn() },
      connect: vi.fn(),
    };
    const oscillator = {
      type: "sine",
      frequency: { value: 0 },
      connect: vi.fn(() => gain),
      start,
      stop,
    };
    const audio = vi.fn(() => ({
      state: "running",
      currentTime: 1,
      createOscillator: () => oscillator,
      createGain: () => gain,
      destination: {},
    }));
    vi.stubGlobal("AudioContext", audio);
    const { playTypingSound } = await import("./typingSound");
    playTypingSound(true);
    expect(audio).toHaveBeenCalledOnce();
    expect(start).toHaveBeenCalledOnce();
    expect(stop).toHaveBeenCalledOnce();
    expect(gain.gain.setValueAtTime).toHaveBeenCalledWith(0.018, 1);
    vi.unstubAllGlobals();
  });
});
