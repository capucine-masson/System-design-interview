import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ProgressBar from "./ProgressBar";

describe("ProgressBar", () => {
  it("expose la progression et le texte", () => {
    render(<ProgressBar maitrisees={3} aRevoir={2} total={10} />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "3");
    expect(bar).toHaveAttribute("aria-valuemax", "10");
    expect(screen.getByText("3/10 maîtrisées · 2 à revoir")).toBeInTheDocument();
  });

  it("gère un thème vide sans division par zéro", () => {
    render(<ProgressBar maitrisees={0} aRevoir={0} total={0} />);
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "0");
  });
});
