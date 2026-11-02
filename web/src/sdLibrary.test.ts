import { describe, expect, it, vi } from "vitest";
import { buildLibraryItems } from "./sdLibrary";

vi.mock("@excalidraw/excalidraw", async () => (await import("./test/mockExcalidraw")).excalidrawModule);

interface Part {
  type: string;
  groupIds: string[];
  customData: { component: string };
  points?: number[][];
}

const parts = (id: string): Part[] => {
  const item = buildLibraryItems().find((candidate) => candidate.id === id);
  return (item?.elements ?? []) as unknown as Part[];
};

describe("bibliothèque de formes préchargée", () => {
  it("propose cylindre, file, service externe et utilisateur", () => {
    expect(buildLibraryItems().map((item) => item.name)).toEqual([
      "Base de données (cylindre)",
      "File / queue",
      "Service externe",
      "Utilisateur",
    ]);
  });

  it("dessine le cylindre : ellipse du dessus, deux flancs, arc du dessous et étiquette", () => {
    const cylinder = parts("lib-database");
    expect(cylinder.filter((p) => p.type === "ellipse")).toHaveLength(1);
    expect(cylinder.filter((p) => p.type === "line")).toHaveLength(3);
    expect(cylinder.filter((p) => p.type === "text")).toHaveLength(1);
    const arc = cylinder.find((p) => p.type === "line" && p.points?.length === 3);
    expect(arc).toBeDefined();
  });

  it("marque chaque forme comme un seul groupe reconnu par la description du schéma", () => {
    const expected: Record<string, string> = {
      "lib-database": "database",
      "lib-queue": "queue",
      "lib-cloud": "cloud",
      "lib-user": "user",
    };
    for (const [id, component] of Object.entries(expected)) {
      const elements = parts(id);
      expect(elements.length).toBeGreaterThan(1);
      for (const element of elements) {
        expect(element.groupIds).toEqual([id]);
        expect(element.customData).toEqual({ component });
      }
    }
  });

  it("donne un identifiant unique à chaque élément de bibliothèque", () => {
    const ids = buildLibraryItems().map((item) => item.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});
