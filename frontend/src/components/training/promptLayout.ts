export type PromptLayoutMode = "short" | "standard" | "passage";

export function getPromptLayoutMode(
  textLength: number,
  lessonKind?: string,
  estimatedDurationSeconds?: number | null,
): PromptLayoutMode {
  if (lessonKind === "passage" || textLength > 220 || (estimatedDurationSeconds ?? 0) > 45) return "passage";
  return textLength > 45 ? "standard" : "short";
}
