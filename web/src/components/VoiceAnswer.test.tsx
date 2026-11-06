import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import VoiceAnswer from "./VoiceAnswer";

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

describe("VoiceAnswer", () => {
  beforeEach(() => {
    speech.state.supported = true;
    speech.state.start.mockClear();
    speech.state.stop.mockClear();
  });

  it("démarre la dictée au clic sur le micro", async () => {
    render(<VoiceAnswer busy={false} onSubmit={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Dicter ma réponse" }));
    expect(speech.state.start).toHaveBeenCalledOnce();
  });

  it("ajoute le texte dicté et l'envoie", async () => {
    const onSubmit = vi.fn().mockResolvedValue(true);
    render(<VoiceAnswer busy={false} onSubmit={onSubmit} />);
    act(() => speech.emitFinal?.("Bonjour"));
    await userEvent.click(screen.getByRole("button", { name: "Envoyer pour correction" }));
    expect(onSubmit).toHaveBeenCalledWith("Bonjour");
  });

  it("sans dictée, explique et laisse taper ; envoi désactivé tant que c'est vide", () => {
    speech.state.supported = false;
    render(<VoiceAnswer busy={false} onSubmit={vi.fn()} />);
    expect(screen.queryByRole("button", { name: "Dicter ma réponse" })).not.toBeInTheDocument();
    expect(screen.getByLabelText("Transcription de ta réponse")).toBeEnabled();
    expect(screen.getByRole("button", { name: "Envoyer pour correction" })).toBeDisabled();
  });

  it("désactive tout pendant la correction", () => {
    render(<VoiceAnswer busy onSubmit={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Correction en cours…" })).toBeDisabled();
    expect(screen.getByLabelText("Transcription de ta réponse")).toBeDisabled();
  });
});
