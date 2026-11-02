import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { ANSWERED, FINISHED, SESSION, WITH_RELANCE } from "../test/managerFixtures";
import ManagerSession from "./ManagerSession";

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

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={["/entretien-manager/sessions/7"]}>
      <Routes>
        <Route path="/entretien-manager/sessions/:id" element={<ManagerSession />} />
      </Routes>
    </MemoryRouter>,
  );

async function typeAndSend(text: string): Promise<void> {
  await userEvent.type(await screen.findByLabelText("Transcription de ta réponse"), text);
  await userEvent.click(screen.getByRole("button", { name: "Envoyer ma réponse" }));
}

describe("ManagerSession", () => {
  beforeEach(() => vi.resetAllMocks());

  it("affiche le scénario et le champ de réponse sans aucun appel IA au chargement", async () => {
    vi.mocked(api.getSession).mockResolvedValue(SESSION);
    renderPage();
    expect(await screen.findByText(SESSION.question.enonce)).toBeInTheDocument();
    expect(screen.getByText("Deux semaines")).toBeInTheDocument();
    expect(screen.getByText("Échange 1 sur 3")).toBeInTheDocument();
    expect(api.sendAnswer).not.toHaveBeenCalled();
    expect(api.requestRelance).not.toHaveBeenCalled();
    expect(api.requestFeedback).not.toHaveBeenCalled();
  });

  it("enchaîne réponse puis relance et affiche la relance du manager", async () => {
    vi.mocked(api.getSession).mockResolvedValue(SESSION);
    vi.mocked(api.sendAnswer).mockResolvedValue(ANSWERED);
    vi.mocked(api.requestRelance).mockResolvedValue(WITH_RELANCE);
    renderPage();
    await typeAndSend("Je lance en périmètre réduit.");
    expect(api.sendAnswer).toHaveBeenCalledWith(7, "Je lance en périmètre réduit.", expect.any(Number));
    expect(await screen.findByText("Que ferais-tu si le client refuse ?")).toBeInTheDocument();
    expect(api.requestRelance).toHaveBeenCalledWith(7);
    expect(screen.getByText("Échange 2 sur 3")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Terminer et obtenir le retour" })).toBeEnabled();
  });

  it("propose de réessayer la relance si elle échoue, sans perdre la réponse", async () => {
    vi.mocked(api.getSession).mockResolvedValue(SESSION);
    vi.mocked(api.sendAnswer).mockResolvedValue(ANSWERED);
    vi.mocked(api.requestRelance)
      .mockRejectedValueOnce(new Error("Mistral est injoignable"))
      .mockResolvedValueOnce(WITH_RELANCE);
    renderPage();
    await typeAndSend("Je lance.");
    expect(await screen.findByText("Mistral est injoignable")).toBeInTheDocument();
    expect(screen.getByText("Je lance en périmètre réduit.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Réessayer la relance" }));
    expect(await screen.findByText("Que ferais-tu si le client refuse ?")).toBeInTheDocument();
  });

  it("garde le texte saisi quand l'enregistrement de la réponse échoue", async () => {
    vi.mocked(api.getSession).mockResolvedValue(SESSION);
    vi.mocked(api.sendAnswer).mockRejectedValue(new Error("Erreur 500"));
    renderPage();
    await typeAndSend("Ma réponse");
    expect(await screen.findByText("Erreur 500")).toBeInTheDocument();
    expect(screen.getByLabelText("Transcription de ta réponse")).toHaveValue("Ma réponse");
    expect(api.requestRelance).not.toHaveBeenCalled();
  });

  it("demande le retour sur action explicite puis l'affiche", async () => {
    vi.mocked(api.getSession).mockResolvedValue(WITH_RELANCE);
    vi.mocked(api.requestFeedback).mockResolvedValue(FINISHED);
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "Terminer et obtenir le retour" }));
    expect(await screen.findByText("Retour du manager")).toBeInTheDocument();
    expect(screen.getByText("Peu de chiffres")).toBeInTheDocument();
    expect(screen.getByText("Je commencerais par cadrer le risque.")).toBeInTheDocument();
    expect(screen.getByText("3.2")).toBeInTheDocument();
    expect(screen.queryByLabelText("Transcription de ta réponse")).not.toBeInTheDocument();
  });

  it("relit une session terminée sans proposer de nouvel appel IA", async () => {
    vi.mocked(api.getSession).mockResolvedValue(FINISHED);
    renderPage();
    expect(await screen.findByText("Retour du manager")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Terminer/ })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Nouvelle question" })).toBeInTheDocument();
  });

  it("limite à trois échanges : plus de champ après la troisième réponse", async () => {
    const third = { ...ANSWERED, answers_count: 3 };
    vi.mocked(api.getSession).mockResolvedValue(third);
    renderPage();
    await screen.findByText(third.question.enonce);
    expect(screen.queryByLabelText("Transcription de ta réponse")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Réessayer la relance" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Terminer et obtenir le retour" })).toBeInTheDocument();
  });

  it("affiche l'erreur de chargement", async () => {
    vi.mocked(api.getSession).mockRejectedValue(new Error("Session introuvable."));
    renderPage();
    await waitFor(() => expect(screen.getByText("Session introuvable.")).toBeInTheDocument());
  });
});
