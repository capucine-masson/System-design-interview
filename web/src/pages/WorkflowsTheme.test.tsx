import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CARD, CARD_2, THEME } from "../test/fixtures";
import WorkflowsTheme from "./WorkflowsTheme";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={["/workflows/transformers"]}>
      <Routes>
        <Route path="/workflows/:slug" element={<WorkflowsTheme />} />
      </Routes>
    </MemoryRouter>,
  );

describe("WorkflowsTheme", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.getWorkflowThemes).mockResolvedValue([THEME]);
    vi.mocked(api.getWorkflowCards).mockResolvedValue([CARD, CARD_2]);
    vi.mocked(api.setWorkflowProgress).mockResolvedValue(undefined);
  });

  it("affiche les cartes et la progression de la catégorie", async () => {
    renderPage();
    expect(await screen.findByRole("button", { name: /Self-attention/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Tokenisation/ })).toBeInTheDocument();
    expect(await screen.findByRole("progressbar")).toHaveAttribute("aria-valuenow", "1");
  });

  it("sauvegarde le statut via l'API Workflows (pas celle des Cours)", async () => {
    renderPage();
    const front = await screen.findByRole("button", { name: /Self-attention/ });
    const article = front.closest("article");
    if (!article) throw new Error("article introuvable");
    await userEvent.click(within(article).getByRole("button", { name: "Maîtrisée" }));
    expect(api.setWorkflowProgress).toHaveBeenCalledWith(1, "maitrisee");
    expect(api.setProgress).not.toHaveBeenCalled();
    await waitFor(() =>
      expect(within(article).getByRole("button", { name: "Maîtrisée" })).toHaveAttribute(
        "aria-pressed",
        "true",
      ),
    );
  });

  it("filtre sur « à revoir »", async () => {
    renderPage();
    await screen.findByRole("button", { name: /Self-attention/ });
    vi.mocked(api.getWorkflowCards).mockResolvedValue([CARD_2]);
    await userEvent.click(screen.getByRole("button", { name: "Filtrer : à revoir" }));
    await waitFor(() =>
      expect(api.getWorkflowCards).toHaveBeenLastCalledWith("transformers", "a_revoir"),
    );
  });
});
