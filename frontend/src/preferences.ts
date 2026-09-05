export const THEMES = ["midnight", "soft-slate", "soft-plum"] as const;
export type ThemeId = (typeof THEMES)[number];
export type Preferences = {
  theme_id: ThemeId;
  sound_enabled: boolean;
  reduce_motion: boolean;
  hand_guidance_enabled: boolean;
};
export const DEFAULT_PREFERENCES: Preferences = {
  theme_id: "midnight",
  sound_enabled: true,
  reduce_motion: false,
  hand_guidance_enabled: true,
};
const KEY = "cadence_preferences_v1";
export function loadPreferences(): Preferences {
  try {
    return {
      ...DEFAULT_PREFERENCES,
      ...JSON.parse(localStorage.getItem(KEY) ?? "{}"),
    };
  } catch {
    return DEFAULT_PREFERENCES;
  }
}
export function applyPreferences(value: Preferences) {
  document.documentElement.dataset.theme = value.theme_id;
  localStorage.setItem(KEY, JSON.stringify(value));
}
