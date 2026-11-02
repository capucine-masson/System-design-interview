import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CARD, CARD_2 } from "../test/fixtures";
import Revision from "./Revision";

vi.mock("../api");

const renderPage = (url = "/cours/revision") =>
  render(
    <MemoryRouter initialEntries={[url]}>
      <Revision />
    </MemoryRouter>,
  );

describe("Revision", () => {
  beforeEach(() => vi.resetAllMocks());

  it("tire une carte puis la suivante en excluant la courante", async () => {
    vi.mocked(api.getRandomCard).mockResolvedValueOnce(CARD).mockResolvedValueOnce(CARD_2);
    renderPage();
    expect(await screen.findByRole("button", { name: /Self-attention/ })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Carte suivante" }));
    expect(await screen.findByRole("button", { name: /Tokenisation/ })).toBeInTheDocument();
    expect(api.getRandomCard).toHaveBeenLastCalledWith({ theme: undefined, statut: undefined, exclude: 1 });
  });

  it("limite le tirage à un thème et aux cartes à revoir", async () => {
    vi.mocked(api.getRandomCard).mockResolvedValue(CARD);
    renderPage("/cours/revision?theme=transformers");
    await screen.findByRole("button", { name: /Self-attention/ });
    await userEvent.click(screen.getByRole("button", { name: "Seulement « à revoir »" }));
    await waitFor(() =>
      expect(api.getRandomCard).toHaveBeenLastCalledWith({
        theme: "transformers",
        statut: "a_revoir",
        exclude: undefined,
      }),
    );
  });

  it("affiche l'état vide quand il n'y a rien à réviser", async () => {
    vi.mocked(api.getRandomCard).mockRejectedValue(new Error("Aucune carte à réviser."));
    renderPage();
    expect(await screen.findByText("Aucune carte à réviser.")).toBeInTheDocument();
  });
});
