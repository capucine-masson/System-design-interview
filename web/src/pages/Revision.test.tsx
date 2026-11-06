import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CARD, CARD_2, REVIEW, THEME } from "../test/fixtures";
import Revision from "./Revision";

vi.mock("../api");
vi.mock("../hooks/useSpeechRecognition", () => ({
  useSpeechRecognition: () => ({
    supported: false,
    listening: false,
    interim: "",
    error: null,
    start: vi.fn(),
    stop: vi.fn(),
  }),
}));

const renderPage = (url = "/cours/revision") =>
  render(
    <MemoryRouter initialEntries={[url]}>
      <Revision />
    </MemoryRouter>,
  );

const start = async (): Promise<void> => {
  await userEvent.click(await screen.findByRole("button", { name: "Commencer" }));
};

const answer = async (text: string): Promise<void> => {
  await userEvent.type(await screen.findByLabelText("Transcription de ta réponse"), text);
  await userEvent.click(screen.getByRole("button", { name: "Envoyer pour correction" }));
};

describe("Revision", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.getThemes).mockResolvedValue([THEME]);
  });

  it("tire 5 cartes parmi tous les thèmes quand on choisit 5", async () => {
    vi.mocked(api.drawCards).mockResolvedValue([CARD, CARD_2]);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "5" }));
    await start();
    expect(api.drawCards).toHaveBeenCalledWith({ theme: undefined, statut: undefined, limit: 5 });
    expect(await screen.findByRole("heading", { name: "Self-attention" })).toBeInTheDocument();
  });

  it("« max » ne limite pas le tirage ; un thème et « à revoir » filtrent", async () => {
    vi.mocked(api.drawCards).mockResolvedValue([CARD]);
    renderPage("/cours/revision?theme=transformers");
    await userEvent.click(await screen.findByRole("button", { name: /Max/ }));
    await userEvent.click(screen.getByRole("button", { name: "Seulement « à revoir »" }));
    await start();
    expect(api.drawCards).toHaveBeenCalledWith({
      theme: "transformers",
      statut: "a_revoir",
      limit: undefined,
    });
  });

  it("« seulement les indispensables » filtre le tirage", async () => {
    vi.mocked(api.drawCards).mockResolvedValue([CARD]);
    renderPage();
    await userEvent.click(await screen.findByRole("checkbox", { name: /indispensables/ }));
    await start();
    expect(api.drawCards).toHaveBeenCalledWith({
      theme: undefined,
      statut: undefined,
      limit: 10,
      essentielle: true,
    });
  });

  it("corrige l'explication puis passe à la carte suivante et termine", async () => {
    vi.mocked(api.drawCards).mockResolvedValue([CARD, CARD_2]);
    vi.mocked(api.reviewCard).mockResolvedValue(REVIEW);
    renderPage();
    await start();
    await answer("Chaque token regarde les autres.");
    expect(api.reviewCard).toHaveBeenCalledWith(1, "Chaque token regarde les autres.");
    expect(await screen.findByText(REVIEW.explication_simple)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Carte suivante" }));
    expect(await screen.findByRole("heading", { name: "Tokenisation" })).toBeInTheDocument();
    await answer("Découper le texte.");
    await userEvent.click(await screen.findByRole("button", { name: "Terminer" }));
    expect(await screen.findByText("Session terminée")).toBeInTheDocument();
  });

  it("garde la réponse et affiche l'erreur si la correction échoue", async () => {
    vi.mocked(api.drawCards).mockResolvedValue([CARD]);
    vi.mocked(api.reviewCard).mockRejectedValue(new Error("Mistral indisponible"));
    renderPage();
    await start();
    await answer("Ma réponse");
    expect(await screen.findByText("Mistral indisponible")).toBeInTheDocument();
    expect(screen.getByLabelText("Transcription de ta réponse")).toHaveValue("Ma réponse");
  });

  it("affiche l'état vide quand il n'y a rien à réviser", async () => {
    vi.mocked(api.drawCards).mockRejectedValue(new Error("Aucune carte à réviser."));
    renderPage();
    await start();
    expect(await screen.findByText("Aucune carte à réviser.")).toBeInTheDocument();
  });
});
