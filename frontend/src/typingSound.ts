let context: AudioContext | null = null;
export function playTypingSound(enabled: boolean, isSpace = false) {
  if (!enabled) return;
  context ??= new AudioContext();
  if (context.state === "suspended") void context.resume();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.type = "sine";
  oscillator.frequency.value = isSpace ? 180 : 230;
  gain.gain.setValueAtTime(0.018, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 0.035);
  oscillator.connect(gain).connect(context.destination);
  oscillator.start();
  oscillator.stop(context.currentTime + 0.04);
}
