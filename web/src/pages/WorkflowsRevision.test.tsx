import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CARD, CARD_2, REVIEW, THEME } from "../test/fixtures";
import WorkflowsRevision from "./WorkflowsRevision";

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

const renderPage = (url = "/workflows/revision") =>
  render(
    <MemoryRouter initialEntries={[url]}>
      <WorkflowsRevision />
    </MemoryRouter>,
  );

const start = async (): Promise<void> => {
  await userEvent.click(await screen.findByRole("button", { name: "Commencer" }));
};

describe("WorkflowsRevision", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.getWorkflowThemes).mockResolvedValue([THEME]);
  });

  it("tire des cartes Workflows, filtrées par catégorie et par statut", async () => {
    vi.mocked(api.drawWorkflowCards).mockResolvedValue([CARD, CARD_2]);
    renderPage("/workflows/revision?theme=transformers");
    await userEvent.click(await screen.findByRole("button", { name: "5" }));
    await userEvent.click(screen.getByRole("button", { name: "Seulement « à revoir »" }));
    await start();
    expect(api.drawWorkflowCards).toHaveBeenCalledWith({
      theme: "transformers",
      statut: "a_revoir",
      limit: 5,
    });
    expect(await screen.findByRole("heading", { name: "Self-attention" })).toBeInTheDocument();
  });

  it("corrige l'explication avec l'API Workflows", async () => {
    vi.mocked(api.drawWorkflowCards).mockResolvedValue([CARD]);
    vi.mocked(api.reviewWorkflowCard).mockResolvedValue(REVIEW);
    renderPage();
    await start();
    await userEvent.type(await screen.findByLabelText("Transcription de ta réponse"), "Je rejoue.");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer pour correction" }));
    expect(api.reviewWorkflowCard).toHaveBeenCalledWith(1, "Je rejoue.");
    expect(api.reviewCard).not.toHaveBeenCalled();
    expect(await screen.findByText(REVIEW.explication_simple)).toBeInTheDocument();
  });

  it("affiche l'état vide quand il n'y a rien à réviser", async () => {
    vi.mocked(api.drawWorkflowCards).mockRejectedValue(new Error("Aucune carte à réviser."));
    renderPage();
    await start();
    expect(await screen.findByText("Aucune carte à réviser.")).toBeInTheDocument();
  });
});
