import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ANSWERED, AWAITING, FINISHED_SD, SD_SESSION } from "../test/sdFixtures";
import type { SdSession } from "../types";
import SdChat from "./SdChat";

const speech = vi.hoisted(() => ({
  state: {
    supported: true,
    listening: false,
    interim: "",
    error: null as string | null,
    start: vi.fn(),
    stop: vi.fn(),
  },
  emitFinal: null as ((text: string) => void) | null,
}));

vi.mock("../hooks/useSpeechRecognition", () => ({
  useSpeechRecognition: (onFinalText: (text: string) => void) => {
    speech.emitFinal = onFinalText;
    return speech.state;
  },
}));

function renderChat(session: SdSession = SD_SESSION, overrides: Partial<React.ComponentProps<typeof SdChat>> = {}) {
  const props = {
    session,
    busy: false,
    error: null,
    onSend: vi.fn().mockResolvedValue(true),
    onRetryReply: vi.fn(),
    ...overrides,
  };
  render(<SdChat {...props} />);
  return props;
}

describe("SdChat", () => {
  beforeEach(() => {
    speech.state.supported = true;
    speech.state.listening = false;
    speech.state.interim = "";
    speech.state.error = null;
    speech.state.start.mockClear();
    speech.state.stop.mockClear();
  });

  it("affiche l'énoncé comme premier message de l'interviewer", () => {
    renderChat();
    expect(screen.getByText(/Une équipe veut un assistant/)).toBeInTheDocument();
    expect(screen.getAllByText("Interviewer").length).toBeGreaterThan(0);
  });

  it("envoie le message tapé avec le bouton, puis vide le champ", async () => {
    const props = renderChat();
    await userEvent.type(screen.getByLabelText("Ton message"), "Quel volume de documents ?");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(props.onSend).toHaveBeenCalledWith("Quel volume de documents ?");
    expect(screen.getByLabelText("Ton message")).toHaveValue("");
  });

  it("envoie avec Entrée mais pas avec Maj+Entrée", async () => {
    const props = renderChat();
    const field = screen.getByLabelText("Ton message");
    await userEvent.type(field, "ligne un{Shift>}{Enter}{/Shift}ligne deux");
    expect(props.onSend).not.toHaveBeenCalled();
    expect(field).toHaveValue("ligne un\nligne deux");
    await userEvent.type(field, "{Enter}");
    expect(props.onSend).toHaveBeenCalledWith("ligne un\nligne deux");
  });

  it("garde le texte quand l'envoi échoue", async () => {
    renderChat(SD_SESSION, { onSend: vi.fn().mockResolvedValue(false) });
    await userEvent.type(screen.getByLabelText("Ton message"), "À conserver");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(screen.getByLabelText("Ton message")).toHaveValue("À conserver");
  });

  it("désactive l'envoi quand le champ est vide", () => {
    renderChat();
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled();
  });

  it("ajoute le texte dicté au champ, modifiable avant l'envoi", async () => {
    const props = renderChat();
    act(() => speech.emitFinal?.("Je voudrais connaître"));
    act(() => speech.emitFinal?.("le volume"));
    const field = screen.getByLabelText("Ton message");
    expect(field).toHaveValue("Je voudrais connaître le volume");
    await userEvent.type(field, " de documents");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer" }));
    expect(props.onSend).toHaveBeenCalledWith("Je voudrais connaître le volume de documents");
  });

  it("démarre la dictée au clic sur le micro", async () => {
    renderChat();
    await userEvent.click(screen.getByRole("button", { name: "Dicter" }));
    expect(speech.state.start).toHaveBeenCalledOnce();
  });

  it("explique l'absence de dictée et laisse taper", async () => {
    speech.state.supported = false;
    renderChat();
    expect(screen.getByText(/Chrome ou Edge/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Dicter/ })).not.toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Ton message"), "ok");
    expect(screen.getByLabelText("Ton message")).toHaveValue("ok");
  });

  it("affiche l'attente de l'interviewer et bloque la saisie pendant l'appel", () => {
    renderChat(AWAITING, { busy: true });
    expect(screen.getByText("L'interviewer réfléchit…")).toBeInTheDocument();
    expect(screen.getByLabelText("Ton message")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Envoyer" })).toBeDisabled();
  });

  it("propose de redemander la réponse si elle a échoué", async () => {
    const props = renderChat(AWAITING, { error: "Quota Mistral dépassé" });
    expect(screen.getByText("Quota Mistral dépassé")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Redemander la réponse/ }));
    expect(props.onRetryReply).toHaveBeenCalledOnce();
  });

  it("autorise un nouveau message une fois l'interviewer répondu", () => {
    renderChat(ANSWERED);
    expect(screen.getByLabelText("Ton message")).toBeEnabled();
    expect(screen.queryByRole("button", { name: /Redemander/ })).not.toBeInTheDocument();
  });

  it("ferme la discussion quand la session est terminée", () => {
    renderChat(FINISHED_SD);
    expect(screen.getByLabelText("Ton message")).toBeDisabled();
    expect(screen.getByText(/discussion est fermée/)).toBeInTheDocument();
  });

  it("indique quand le nombre maximal de messages est atteint", () => {
    renderChat({ ...ANSWERED, user_messages: 40 });
    expect(screen.getByLabelText("Ton message")).toBeDisabled();
    expect(screen.getByText(/Nombre maximal de messages/)).toBeInTheDocument();
  });
});
