import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { ANSWERED, AWAITING, FINISHED_SD, SD_SESSION, STORED_SCENE } from "../test/sdFixtures";
import SystemDesignSession from "./SystemDesignSession";

const canvas = vi.hoisted(() => ({
  flush: vi.fn().mockResolvedValue(undefined),
  props: null as { initialScene: unknown; readOnly: boolean; sessionId: number } | null,
}));

vi.mock("../api");
vi.mock("../components/SdCanvas", async () => {
  const React = await import("react");
  return {
    default: (props: {
      initialScene: unknown;
      readOnly: boolean;
      sessionId: number;
      ref?: React.Ref<{ flush: () => Promise<void> }>;
    }) => {
      canvas.props = props;
      React.useImperativeHandle(props.ref, () => ({ flush: canvas.flush }));
      return <div data-testid="canvas">{props.readOnly ? "lecture seule" : "éditable"}</div>;
    },
  };
});
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
    <MemoryRouter initialEntries={["/system-design/sessions/5"]}>
      <Routes>
        <Route path="/system-design/sessions/:id" element={<SystemDesignSession />} />
      </Routes>
    </MemoryRouter>,
  );

describe("SystemDesignSession", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    canvas.flush.mockResolvedValue(undefined);
    canvas.props = null;
    vi.mocked(api.getSdSession).mockResolvedValue(SD_SESSION);
    vi.mocked(api.getScene).mockResolvedValue(null);
    vi.mocked(api.putElapsed).mockResolvedValue(undefined);
  });

  it("affiche le brief, le chat, le minuteur et le canvas, sans aucun appel IA", async () => {
    renderPage();
    expect(await screen.findByRole("heading", { name: "Assistant documentaire interne" })).toBeInTheDocument();
    expect(screen.getByText(/Pose-moi tes questions/)).toBeInTheDocument();
    expect(screen.getByRole("timer")).toBeInTheDocument();
    expect(screen.getByTestId("canvas")).toHaveTextContent("éditable");
    expect(api.requestSdReply).not.toHaveBeenCalled();
    expect(api.postSdMessage).not.toHaveBeenCalled();
  });

  it("retrouve tout en rouvrant la session : chat, schéma et temps écoulé", async () => {
    vi.mocked(api.getSdSession).mockResolvedValue(ANSWERED);
    vi.mocked(api.getScene).mockResolvedValue(STORED_SCENE);
    renderPage();
    expect(await screen.findByText("Quel volume de documents ?")).toBeInTheDocument();
    expect(screen.getByText("Environ douze millions de pages.")).toBeInTheDocument();
    expect(canvas.props?.initialScene).toEqual(STORED_SCENE);
    expect(canvas.props?.sessionId).toBe(5);
    expect(screen.getByRole("timer")).toHaveTextContent("35:00"); // 45 min - 600 s déjà écoulées
  });

  it("enregistre le message puis demande la réponse de l'interviewer", async () => {
    vi.mocked(api.postSdMessage).mockResolvedValue(AWAITING);
    vi.mocked(api.requestSdReply).mockResolvedValue(ANSWERED);
    renderPage();
    await userEvent.type(await screen.findByLabelText("Ton message"), "Quel volume de documents ?");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(api.postSdMessage).toHaveBeenCalledWith(5, "Quel volume de documents ?", expect.any(Number));
    expect(await screen.findByText("Environ douze millions de pages.")).toBeInTheDocument();
    expect(api.requestSdReply).toHaveBeenCalledWith(5);
  });

  it("garde le message et propose de redemander quand la réponse échoue", async () => {
    vi.mocked(api.postSdMessage).mockResolvedValue(AWAITING);
    vi.mocked(api.requestSdReply)
      .mockRejectedValueOnce(new Error("Mistral est injoignable"))
      .mockResolvedValueOnce(ANSWERED);
    renderPage();
    await userEvent.type(await screen.findByLabelText("Ton message"), "Quel volume de documents ?");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(await screen.findByText("Mistral est injoignable")).toBeInTheDocument();
    expect(screen.getByText("Quel volume de documents ?")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Redemander la réponse/ }));
    expect(await screen.findByText("Environ douze millions de pages.")).toBeInTheDocument();
  });

  it("n'appelle pas l'IA si l'enregistrement du message échoue", async () => {
    vi.mocked(api.postSdMessage).mockRejectedValue(new Error("Erreur 500"));
    renderPage();
    await userEvent.type(await screen.findByLabelText("Ton message"), "Bonjour");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(await screen.findByText("Erreur 500")).toBeInTheDocument();
    expect(api.requestSdReply).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Ton message")).toHaveValue("Bonjour");
  });

  it("demande confirmation, enregistre le schéma, puis termine et verrouille la session", async () => {
    const order: string[] = [];
    canvas.flush.mockImplementation(async () => {
      order.push("flush");
    });
    vi.mocked(api.finishSdSession).mockImplementation(async () => {
      order.push("finish");
      return FINISHED_SD;
    });
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "Terminer et obtenir la correction" }));
    expect(api.finishSdSession).not.toHaveBeenCalled();
    await userEvent.click(screen.getByRole("button", { name: "Oui, terminer" }));
    expect(await screen.findByText(/La correction détaillée arrivera/)).toBeInTheDocument();
    expect(order).toEqual(["flush", "finish"]); // le dernier schéma est enregistré avant la clôture
    expect(screen.getByTestId("canvas")).toHaveTextContent("lecture seule");
    expect(screen.getByLabelText("Ton message")).toBeDisabled();
    expect(api.requestSdReply).not.toHaveBeenCalled();
  });

  it("peut annuler la fin de session", async () => {
    renderPage();
    await userEvent.click(await screen.findByRole("button", { name: "Terminer et obtenir la correction" }));
    await userEvent.click(screen.getByRole("button", { name: "Annuler" }));
    expect(api.finishSdSession).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Terminer et obtenir la correction" })).toBeInTheDocument();
  });

  it("rouvre une session terminée en lecture seule", async () => {
    vi.mocked(api.getSdSession).mockResolvedValue(FINISHED_SD);
    vi.mocked(api.getScene).mockResolvedValue(STORED_SCENE);
    renderPage();
    expect(await screen.findByText(/La correction détaillée arrivera/)).toBeInTheDocument();
    expect(screen.getByTestId("canvas")).toHaveTextContent("lecture seule");
  });

  it("affiche l'erreur de chargement", async () => {
    vi.mocked(api.getSdSession).mockRejectedValue(new Error("Session introuvable."));
    renderPage();
    await waitFor(() => expect(screen.getByText("Session introuvable.")).toBeInTheDocument());
  });
});
