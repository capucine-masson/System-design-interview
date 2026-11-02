import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import AnswerComposer from "./AnswerComposer";

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

describe("AnswerComposer", () => {
  beforeEach(() => {
    speech.state.supported = true;
    speech.state.listening = false;
    speech.state.interim = "";
    speech.state.error = null;
    speech.state.start.mockClear();
    speech.state.stop.mockClear();
  });

  afterEach(() => vi.useRealTimers());

  it("propose la dictée quand le navigateur la supporte, et la démarre au clic", async () => {
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: "Dicter ma réponse" }));
    expect(speech.state.start).toHaveBeenCalledOnce();
    expect(screen.queryByText(/n'est pas disponible/)).not.toBeInTheDocument();
  });

  it("explique quoi faire quand la dictée n'est pas supportée et laisse taper", async () => {
    speech.state.supported = false;
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    expect(screen.getByText(/Utilise Chrome ou Edge/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /dicter|dictée/i })).not.toBeInTheDocument();
    await userEvent.type(screen.getByLabelText("Transcription de ta réponse"), "Je tape");
    expect(screen.getByLabelText("Transcription de ta réponse")).toHaveValue("Je tape");
  });

  it("affiche le texte dicté en direct, modifiable avant l'envoi", async () => {
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    act(() => speech.emitFinal?.("Je pense que"));
    act(() => speech.emitFinal?.("nous devons lancer"));
    const field = screen.getByLabelText("Transcription de ta réponse");
    expect(field).toHaveValue("Je pense que nous devons lancer");
    await userEvent.type(field, " vite");
    expect(field).toHaveValue("Je pense que nous devons lancer vite");
  });

  it("montre le texte provisoire et les erreurs de dictée", () => {
    speech.state.interim = "en cours de dictée";
    speech.state.error = "Accès au micro refusé";
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    expect(screen.getByText("en cours de dictée")).toBeInTheDocument();
    expect(screen.getByText("Accès au micro refusé")).toBeInTheDocument();
  });

  it("désactive l'envoi tant que le champ est vide ou pendant un appel", async () => {
    const { rerender } = render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    const send = screen.getByRole("button", { name: "Envoyer ma réponse" });
    expect(send).toBeDisabled();
    await userEvent.type(screen.getByLabelText("Transcription de ta réponse"), "ok");
    expect(send).toBeEnabled();
    rerender(<AnswerComposer busy onSubmit={vi.fn()} />);
    expect(screen.getByRole("button", { name: "Envoyer ma réponse" })).toBeDisabled();
  });

  it("envoie le texte et la durée, puis vide le champ si la réponse est enregistrée", async () => {
    const onSubmit = vi.fn().mockResolvedValue(true);
    render(<AnswerComposer busy={false} onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText("Transcription de ta réponse"), "  Ma réponse  ");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer ma réponse" }));
    expect(onSubmit).toHaveBeenCalledWith("Ma réponse", expect.any(Number));
    expect(speech.state.stop).toHaveBeenCalled();
    expect(screen.getByLabelText("Transcription de ta réponse")).toHaveValue("");
  });

  it("garde le texte si l'envoi échoue", async () => {
    const onSubmit = vi.fn().mockResolvedValue(false);
    render(<AnswerComposer busy={false} onSubmit={onSubmit} />);
    await userEvent.type(screen.getByLabelText("Transcription de ta réponse"), "À conserver");
    await userEvent.click(screen.getByRole("button", { name: "Envoyer ma réponse" }));
    expect(screen.getByLabelText("Transcription de ta réponse")).toHaveValue("À conserver");
  });

  it("affiche le chronomètre à 0:00 avec l'objectif de durée", () => {
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    expect(screen.getByRole("timer")).toHaveTextContent("0:00");
    expect(screen.getByText(/objectif 2:00 à 3:00/)).toBeInTheDocument();
  });

  it("fait avancer le chrono après la première frappe", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    render(<AnswerComposer busy={false} onSubmit={vi.fn()} />);
    await userEvent.type(screen.getByLabelText("Transcription de ta réponse"), "x", {
      advanceTimers: vi.advanceTimersByTime,
    });
    act(() => {
      vi.advanceTimersByTime(65_000);
    });
    expect(screen.getByRole("timer")).toHaveTextContent("1:05");
  });
});
