import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BUNDLE } from "../test/sdFixtures";
import type { CorrectionBundle } from "../types";
import SdCorrectionView from "./SdCorrectionView";

describe("SdCorrectionView", () => {
  it("affiche le verdict, la moyenne et les notes par étape", () => {
    render(<SdCorrectionView bundle={BUNDLE} />);
    expect(screen.getByText("Bonne structure mais peu de chiffres.")).toBeInTheDocument();
    expect(screen.getByText("2.7")).toBeInTheDocument();
    expect(screen.getAllByRole("progressbar")).toHaveLength(6);
    expect(screen.getByText("Clarification du besoin")).toBeInTheDocument();
    expect(screen.getByText("4/5")).toBeInTheDocument();
    expect(screen.getByText("1/5")).toBeInTheDocument();
  });

  it("liste points forts, points faibles, composants manquants et conseils", () => {
    render(<SdCorrectionView bundle={BUNDLE} />);
    expect(screen.getByText("Bonnes questions de départ")).toBeInTheDocument();
    expect(screen.getByText("Évaluation oubliée")).toBeInTheDocument();
    expect(screen.getByText("Reranker")).toBeInTheDocument();
    expect(screen.getByText("Chiffre le dimensionnement")).toBeInTheDocument();
  });

  it("révèle les détails cachés en distinguant obtenus et non demandés", () => {
    render(<SdCorrectionView bundle={BUNDLE} />);
    expect(screen.getByText("2 détails sur 3 n'ont pas été demandés.")).toBeInTheDocument();
    const found = screen.getByText("Volumétrie").closest("li");
    const missed = screen.getByText("Budget").closest("li");
    expect(within(found as HTMLElement).getByText("Obtenu")).toBeInTheDocument();
    expect(within(found as HTMLElement).getByText(/12 millions de pages/)).toBeInTheDocument();
    expect(within(missed as HTMLElement).getByText("Non demandé")).toBeInTheDocument();
    expect(within(missed as HTMLElement).getByText(/30 000 euros par mois/)).toBeInTheDocument();
  });

  it("accorde le message au singulier et félicite quand tout a été obtenu", () => {
    const one: CorrectionBundle = {
      ...BUNDLE,
      details: [
        { sujet: "A", valeur: "1", decouvert: true },
        { sujet: "B", valeur: "2", decouvert: false },
      ],
    };
    const { rerender } = render(<SdCorrectionView bundle={one} />);
    expect(screen.getByText("1 détail sur 2 n'a pas été demandé.")).toBeInTheDocument();
    rerender(<SdCorrectionView bundle={{ ...BUNDLE, details: [{ sujet: "A", valeur: "1", decouvert: true }] }} />);
    expect(screen.getByText(/Tu as obtenu tous les détails/)).toBeInTheDocument();
  });

  it("présente la solution de référence : schéma, composants, parcours, compromis, pièges", () => {
    render(<SdCorrectionView bundle={BUNDLE} />);
    expect(screen.getByRole("img", { name: /Schéma/ })).toBeInTheDocument();
    expect(screen.getByText("Point d'entrée", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("Recherche vectorielle")).toBeInTheDocument();
    expect(screen.getByText(/plutôt que Recherche exacte/)).toBeInTheDocument();
    expect(screen.getByText("Ignorer les droits d'accès")).toBeInTheDocument();
    expect(screen.getByText("Environ 1 To d'index")).toBeInTheDocument();
  });

  it("n'affiche pas de schéma quand la référence n'en a pas d'exploitable", () => {
    const bundle = { ...BUNDLE, reference: { ...BUNDLE.reference, diagramme: null } };
    render(<SdCorrectionView bundle={bundle} />);
    expect(screen.queryByRole("img", { name: /Schéma/ })).not.toBeInTheDocument();
    expect(screen.getByText("Solution de référence")).toBeInTheDocument();
  });
});
