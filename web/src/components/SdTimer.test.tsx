import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { currentPhaseIndex, PHASES } from "../sdPhases";
import SdTimer from "./SdTimer";

const MIN = 60;

describe("SdTimer", () => {
  it("affiche 45:00 au départ et l'étape « Clarifier » en cours", () => {
    render(<SdTimer elapsed={0} />);
    expect(screen.getByRole("timer")).toHaveTextContent("45:00");
    expect(screen.getByText("Clarifier")).toHaveAttribute("aria-current", "step");
  });

  it("décompte le temps restant", () => {
    render(<SdTimer elapsed={12 * MIN + 30} />);
    expect(screen.getByRole("timer")).toHaveTextContent("32:30");
  });

  it("liste toutes les étapes conseillées", () => {
    render(<SdTimer elapsed={0} />);
    for (const label of [
      "Clarifier",
      "Hypothèses",
      "Schéma",
      "Zoom",
      "Compromis",
      "Évaluation et monitoring",
      "Conclusion",
    ]) {
      expect(screen.getByText(label)).toBeInTheDocument();
    }
  });

  it("met en avant l'étape correspondant au temps écoulé", () => {
    render(<SdTimer elapsed={27 * MIN} />);
    expect(screen.getByText("Zoom")).toHaveAttribute("aria-current", "step");
    expect(screen.getByText("Clarifier")).not.toHaveAttribute("aria-current");
  });

  it("signale le dépassement sans bloquer", () => {
    render(<SdTimer elapsed={47 * MIN + 5} />);
    expect(screen.getByRole("timer")).toHaveTextContent("+2:05");
    expect(screen.getByText("temps dépassé")).toBeInTheDocument();
    expect(screen.getByText("Conclusion")).toHaveAttribute("aria-current", "step");
  });
});

describe("currentPhaseIndex", () => {
  it("change d'étape aux minutes prévues", () => {
    const starts = PHASES.map((phase) => currentPhaseIndex(phase.startMinute * MIN));
    expect(starts).toEqual(PHASES.map((_, index) => index));
    expect(currentPhaseIndex(9 * MIN + 59)).toBe(1);
  });
});
