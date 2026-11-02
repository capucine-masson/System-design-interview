import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CARD, CARD_2, THEME } from "../test/fixtures";
import CoursTheme from "./CoursTheme";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={["/cours/transformers"]}>
      <Routes>
        <Route path="/cours/:slug" element={<CoursTheme />} />
      </Routes>
    </MemoryRouter>,
  );

async function selfAttentionArticle(): Promise<HTMLElement> {
  const front = await screen.findByRole("button", { name: /Self-attention/ });
  const article = front.closest("article");
  if (!article) throw new Error("article introuvable");
  return article;
}

describe("CoursTheme", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.getThemes).mockResolvedValue([THEME]);
    vi.mocked(api.getCards).mockResolvedValue([CARD, CARD_2]);
    vi.mocked(api.setProgress).mockResolvedValue(undefined);
  });

  it("affiche la grille de cartes, la barre de progression et la source", async () => {
    renderPage();
    expect(await screen.findByRole("button", { name: /Self-attention/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Tokenisation/ })).toBeInTheDocument();
    expect(await screen.findByRole("progressbar")).toHaveAttribute("aria-valuenow", "1");
    const [themeSource] = screen.getAllByRole("link", { name: "The Illustrated Transformer" });
    expect(themeSource).toHaveAttribute("href", "https://example.org/source");
  });

  it("sauvegarde le statut puis met à jour la carte et la progression", async () => {
    renderPage();
    const article = await selfAttentionArticle();
    vi.mocked(api.getThemes).mockResolvedValue([{ ...THEME, maitrisees: 2, a_revoir: 0 }]);
    await userEvent.click(within(article).getByRole("button", { name: "Maîtrisée" }));
    expect(api.setProgress).toHaveBeenCalledWith(1, "maitrisee");
    await waitFor(() =>
      expect(within(article).getByRole("button", { name: "Maîtrisée" })).toHaveAttribute("aria-pressed", "true"),
    );
    await waitFor(() => expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "2"));
  });

  it("filtre sur « à revoir »", async () => {
    renderPage();
    await selfAttentionArticle();
    vi.mocked(api.getCards).mockResolvedValue([CARD_2]);
    await userEvent.click(screen.getByRole("button", { name: "Filtrer : à revoir" }));
    await waitFor(() => expect(api.getCards).toHaveBeenLastCalledWith("transformers", "a_revoir"));
    expect(await screen.findByRole("button", { name: /Tokenisation/ })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Self-attention/ })).not.toBeInTheDocument();
  });

  it("affiche l'état vide du filtre", async () => {
    renderPage();
    await selfAttentionArticle();
    vi.mocked(api.getCards).mockResolvedValue([]);
    await userEvent.click(screen.getByRole("button", { name: "Filtrer : à revoir" }));
    expect(await screen.findByText("Rien à revoir")).toBeInTheDocument();
  });

  it("affiche l'erreur si la sauvegarde échoue", async () => {
    vi.mocked(api.setProgress).mockRejectedValue(new Error("Carte introuvable."));
    renderPage();
    const article = await selfAttentionArticle();
    await userEvent.click(within(article).getByRole("button", { name: "À revoir" }));
    expect(await screen.findByText("Carte introuvable.")).toBeInTheDocument();
    expect(within(article).getByRole("button", { name: "À revoir" })).toHaveAttribute("aria-pressed", "false");
  });
});
