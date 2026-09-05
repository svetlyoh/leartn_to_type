import runner01 from "../../assets/characters/runner-01.svg";
import runner02 from "../../assets/characters/runner-02.svg";
import focus01 from "../../assets/characters/focus-01.svg";
import focus02 from "../../assets/characters/focus-02.svg";
export const CHARACTERS = [
  {
    id: "runner_01",
    name: "Stride",
    image: runner01,
    trait: "Steady rhythm",
    help: "A steady, balanced training style built around smooth, repeatable timing. Character style only — it does not change your curriculum or scoring.",
  },
  {
    id: "runner_02",
    name: "Flux",
    image: runner02,
    trait: "Quick recovery",
    help: "Represents resetting quickly after a mistake and finding your rhythm again. Character style only — it does not change your curriculum or scoring.",
  },
  {
    id: "focus_01",
    name: "Vector",
    image: focus01,
    trait: "Clean precision",
    help: "Represents accurate finger placement and controlled movement before speed. Character style only — it does not change your curriculum or scoring.",
  },
  {
    id: "focus_02",
    name: "Nova",
    image: focus02,
    trait: "Calm focus",
    help: "Represents relaxed concentration and staying composed through longer practice. Character style only — it does not change your curriculum or scoring.",
  },
] as const;
export const CHARACTER_IDS = new Set(CHARACTERS.map((c) => c.id));
