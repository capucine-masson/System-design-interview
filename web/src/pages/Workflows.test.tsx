import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { THEME } from "../test/fixtures";
import Workflows from "./Workflows";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter>
      <Workflows />
    </MemoryRouter>,
  );

describe("Workflows", () => {
  beforeEach(() => vi.resetAllMocks());

  it("liste les catégories avec leur progression et mène vers /workflows", async () => {
    vi.mocked(api.getWorkflowThemes).mockResolvedValue([THEME]);
    renderPage();
    expect(await screen.findByRole("heading", { name: "Transformers" })).toBeInTheDocument();
    expect(screen.getByText("1/2 maîtrisées · 1 à revoir")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Révision aléatoire" })).toHaveAttribute(
      "href",
      "/workflows/revision",
    );
  });

  it("affiche l'état vide", async () => {
    vi.mocked(api.getWorkflowThemes).mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText("Aucune catégorie")).toBeInTheDocument();
  });

  it("affiche l'erreur de l'API", async () => {
    vi.mocked(api.getWorkflowThemes).mockRejectedValue(new Error("API injoignable"));
    renderPage();
    expect(await screen.findByText("API injoignable")).toBeInTheDocument();
  });

  it("coche une catégorie via l'API Workflows (pas celle des Cours)", async () => {
    vi.mocked(api.getWorkflowThemes).mockResolvedValue([THEME]);
    vi.mocked(api.setWorkflowThemeDone).mockResolvedValue(undefined);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "Marquer ce thème comme maîtrisé" }));
    expect(api.setWorkflowThemeDone).toHaveBeenCalledWith("transformers", true);
    expect(api.setThemeDone).not.toHaveBeenCalled();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Retirer la coche de ce thème" })).toBeInTheDocument(),
    );
  });
});
