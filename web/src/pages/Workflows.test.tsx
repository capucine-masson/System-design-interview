import { render, screen } from "@testing-library/react";
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
});
