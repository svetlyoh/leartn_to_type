import { describe, expect, it } from "vitest";
import { getPromptLayoutMode } from "./promptLayout";

describe("prompt layout", () => {
  it("classifies short, standard, and passage prompts centrally", () => {
    expect(getPromptLayoutMode(45)).toBe("short");
    expect(getPromptLayoutMode(80)).toBe("standard");
    expect(getPromptLayoutMode(221)).toBe("passage");
    expect(getPromptLayoutMode(20, "passage")).toBe("passage");
    expect(getPromptLayoutMode(20, "drill", 46)).toBe("passage");
  });
});
