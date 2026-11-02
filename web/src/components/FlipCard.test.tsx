import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { CARD } from "../test/fixtures";
import FlipCard from "./FlipCard";

describe("FlipCard", () => {
  it("montre le titre sans pop-up au départ", () => {
    render(<FlipCard card={CARD} pending={false} onProgress={vi.fn()} />);
    expect(screen.getByRole("button", { name: /Self-attention/ })).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("ouvre une pop-up au clic et affiche explication, points, schéma et source", async () => {
    render(<FlipCard card={CARD} pending={false} onProgress={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /Self-attention/ }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Chaque token pondère les autres.")).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(CARD.points.length);
    expect(screen.getByRole("img", { name: /Schéma/ })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "The Illustrated Transformer" })).toHaveAttribute(
      "href",
      "https://example.org/source",
    );
  });

  it("ferme la pop-up avec « Fermer » ou Échap", async () => {
    render(<FlipCard card={CARD} pending={false} onProgress={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /Self-attention/ }));
    await userEvent.click(screen.getByRole("button", { name: "Fermer" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Self-attention/ }));
    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("envoie le statut choisi, et null quand on clique le statut actif", async () => {
    const onProgress = vi.fn();
    const { rerender } = render(<FlipCard card={CARD} pending={false} onProgress={onProgress} />);
    await userEvent.click(screen.getByRole("button", { name: "Maîtrisée" }));
    expect(onProgress).toHaveBeenLastCalledWith(CARD, "maitrisee");

    const mastered = { ...CARD, statut: "maitrisee" as const };
    rerender(<FlipCard card={mastered} pending={false} onProgress={onProgress} />);
    expect(screen.getByRole("button", { name: "Maîtrisée" })).toHaveAttribute("aria-pressed", "true");
    await userEvent.click(screen.getByRole("button", { name: "Maîtrisée" }));
    expect(onProgress).toHaveBeenLastCalledWith(mastered, null);
  });

  it("désactive les boutons pendant l'appel", () => {
    render(<FlipCard card={CARD} pending onProgress={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Maîtrisée" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "À revoir" })).toBeDisabled();
  });

  it("affiche une source sans lien quand il n'y a pas d'URL", async () => {
    const card = { ...CARD, source_url: null, source_label: "DDIA, ch. 5" };
    render(<FlipCard card={card} pending={false} onProgress={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: /Self-attention/ }));
    expect(screen.getByText(/DDIA, ch. 5/)).toBeInTheDocument();
    expect(screen.queryByRole("link")).not.toBeInTheDocument();
  });
});
