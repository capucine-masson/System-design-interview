import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { SUMMARY } from "../test/managerFixtures";
import ManagerHistory from "./ManagerHistory";

vi.mock("../api");

const renderIt = () =>
  render(
    <MemoryRouter>
      <ManagerHistory />
    </MemoryRouter>,
  );

describe("ManagerHistory", () => {
  beforeEach(() => vi.resetAllMocks());

  it("liste les sessions avec leurs notes et un lien pour les relire", async () => {
    vi.mocked(api.listSessions).mockResolvedValue([SUMMARY]);
    renderIt();
    const link = await screen.findByRole("link", { name: /Lances-tu le modèle/ });
    expect(link).toHaveAttribute("href", "/entretien-manager/sessions/7");
    expect(screen.getByText("3.2")).toBeInTheDocument();
    expect(screen.getByText("Clarté")).toBeInTheDocument();
    expect(screen.getAllByText("4")).toHaveLength(2);
  });

  it("indique qu'il faut deux entretiens notés pour voir une évolution", async () => {
    vi.mocked(api.listSessions).mockResolvedValue([SUMMARY]);
    renderIt();
    expect(await screen.findByText(/au moins deux entretiens/)).toBeInTheDocument();
  });

  it("trace la courbe d'évolution avec deux sessions notées", async () => {
    vi.mocked(api.listSessions).mockResolvedValue([
      { ...SUMMARY, id: 8, moyenne: 4 },
      SUMMARY,
    ]);
    renderIt();
    expect(await screen.findByRole("img", { name: "Évolution de la moyenne des notes" })).toBeInTheDocument();
  });

  it("affiche « en cours » et des tirets pour une session sans retour", async () => {
    vi.mocked(api.listSessions).mockResolvedValue([
      { ...SUMMARY, statut: "en_cours", notes: null, moyenne: null },
    ]);
    renderIt();
    expect(await screen.findByText(/en cours/)).toBeInTheDocument();
    expect(screen.getAllByText("–").length).toBeGreaterThan(1);
  });

  it("affiche l'état vide et l'erreur", async () => {
    vi.mocked(api.listSessions).mockResolvedValueOnce([]);
    const { unmount } = renderIt();
    expect(await screen.findByText("Aucune session")).toBeInTheDocument();
    unmount();
    vi.mocked(api.listSessions).mockRejectedValueOnce(new Error("API injoignable"));
    renderIt();
    expect(await screen.findByText("API injoignable")).toBeInTheDocument();
  });
});
