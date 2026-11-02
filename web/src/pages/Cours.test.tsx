import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { THEME } from "../test/fixtures";
import Cours from "./Cours";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter>
      <Cours />
    </MemoryRouter>,
  );

describe("Cours", () => {
  beforeEach(() => vi.resetAllMocks());

  it("liste les thèmes avec leur progression", async () => {
    vi.mocked(api.getThemes).mockResolvedValue([THEME]);
    renderPage();
    expect(await screen.findByRole("heading", { name: "Transformers" })).toBeInTheDocument();
    expect(screen.getByText("1/2 maîtrisées · 1 à revoir")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Révision aléatoire" })).toHaveAttribute("href", "/cours/revision");
  });

  it("affiche l'état vide", async () => {
    vi.mocked(api.getThemes).mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText("Aucun thème")).toBeInTheDocument();
  });

  it("affiche l'erreur de l'API", async () => {
    vi.mocked(api.getThemes).mockRejectedValue(new Error("API injoignable"));
    renderPage();
    expect(await screen.findByText("API injoignable")).toBeInTheDocument();
  });
});
