import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

  it("coche un thème à la main sans naviguer, et enregistre en base", async () => {
    vi.mocked(api.getThemes).mockResolvedValue([THEME]);
    vi.mocked(api.setThemeDone).mockResolvedValue(undefined);
    renderPage();
    const check = await screen.findByRole("button", { name: "Marquer ce thème comme maîtrisé" });
    expect(check).toHaveAttribute("aria-pressed", "false");
    await userEvent.click(check);
    expect(api.setThemeDone).toHaveBeenCalledWith("transformers", true);
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Retirer la coche de ce thème" })).toHaveAttribute(
        "aria-pressed",
        "true",
      ),
    );
  });

  it("affiche l'erreur et garde le rond décoché si la sauvegarde échoue", async () => {
    vi.mocked(api.getThemes).mockResolvedValue([THEME]);
    vi.mocked(api.setThemeDone).mockRejectedValue(new Error("Échec réseau"));
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "Marquer ce thème comme maîtrisé" }));
    expect(await screen.findByText("Échec réseau")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Marquer ce thème comme maîtrisé" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });
});
