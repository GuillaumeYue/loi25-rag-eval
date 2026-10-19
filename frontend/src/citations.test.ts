import { describe, expect, it } from "vitest";
import { citedNumbers, splitAnswer } from "./citations";

describe("splitAnswer", () => {
  it("returns plain text untouched", () => {
    expect(splitAnswer("Bonjour.")).toEqual([{ kind: "text", value: "Bonjour." }]);
  });

  it("extracts a single citation", () => {
    expect(splitAnswer("Le délai est de 30 jours [1].")).toEqual([
      { kind: "text", value: "Le délai est de 30 jours " },
      { kind: "cite", n: 1 },
      { kind: "text", value: "." },
    ]);
  });

  it("handles adjacent citations and a citation at the start", () => {
    expect(splitAnswer("[2][3] texte")).toEqual([
      { kind: "cite", n: 2 },
      { kind: "cite", n: 3 },
      { kind: "text", value: " texte" },
    ]);
  });

  it("ignores brackets that are not numbers", () => {
    expect(splitAnswer("[Réponse tronquée] et [a]")).toEqual([
      { kind: "text", value: "[Réponse tronquée] et [a]" },
    ]);
  });

  it("collects the set of cited numbers", () => {
    expect([...citedNumbers("a [1] b [3] c [1]")].sort()).toEqual([1, 3]);
    expect(citedNumbers("rien").size).toBe(0);
  });
});
