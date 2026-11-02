import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Diagram as DiagramData } from "../types";
import Diagram from "./Diagram";

const SIMPLE: DiagramData = {
  nodes: [
    { id: "a", label: "Entrée", col: 0, row: 0 },
    { id: "b", label: "Sortie", col: 1, row: 0 },
  ],
  edges: [{ source: "a", target: "b", label: null }],
};

describe("Diagram", () => {
  it("rend un libellé par boîte et une flèche par lien", () => {
    const { container } = render(<Diagram diagram={SIMPLE} />);
    expect(screen.getByText("Entrée")).toBeInTheDocument();
    expect(screen.getByText("Sortie")).toBeInTheDocument();
    expect(container.querySelectorAll("path.diagram-edge")).toHaveLength(1);
  });

  it("rend le libellé d'une flèche et gère un arc de retour", () => {
    const diagram: DiagramData = {
      ...SIMPLE,
      edges: [
        { source: "a", target: "b", label: "aller" },
        { source: "b", target: "a", label: "boucle" },
      ],
    };
    const { container } = render(<Diagram diagram={diagram} />);
    expect(screen.getByText("boucle")).toBeInTheDocument();
    expect(container.querySelectorAll("path.diagram-edge")).toHaveLength(2);
  });
});
