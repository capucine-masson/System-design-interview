import { useEffect, useRef, useState } from "react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import type { SdSession } from "../types";

const MAX_MESSAGE_CHARS = 2000;

interface SdChatProps {
  session: SdSession;
  busy: boolean;
  error: string | null;
  /** Retourne true si le message a bien été enregistré (le champ est alors vidé). */
  onSend: (text: string) => Promise<boolean>;
  onRetryReply: () => void;
}

export default function SdChat({ session, busy, error, onSend, onRetryReply }: SdChatProps) {
  const [text, setText] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const speech = useSpeechRecognition((finalText) =>
    setText((current) => (current ? `${current} ${finalText}` : finalText)),
  );
  const finished = session.statut === "terminee";
  const limitReached = session.user_messages >= session.max_user_messages;
  const canWrite = !finished && !limitReached && !session.awaiting_reply;

  useEffect(() => {
    bottomRef.current?.scrollIntoView?.({ block: "end" });
  }, [session.messages.length, busy]);

  const submit = async (): Promise<void> => {
    speech.stop();
    if (await onSend(text.trim())) setText("");
  };

  return (
    <section className="card sd-chat" aria-label="Discussion avec l'interviewer">
      <ol className="sd-messages" aria-live="polite">
        {session.messages.map((message) => (
          <li key={message.id} className={`msg msg-${message.role}`}>
            <p className="msg-author muted">{message.role === "user" ? "Toi" : "Interviewer"}</p>
            <p className="msg-text">{message.content}</p>
          </li>
        ))}
        {busy && (
          <li className="msg msg-assistant muted" role="status">
            L&apos;interviewer réfléchit…
          </li>
        )}
        <div ref={bottomRef} />
      </ol>
      {error && <div className="notice notice-error">{error}</div>}
      {session.awaiting_reply && !busy && !finished && (
        <button type="button" className="btn" onClick={onRetryReply}>
          Redemander la réponse de l&apos;interviewer
        </button>
      )}
      {finished && <p className="muted">Session terminée : la discussion est fermée.</p>}
      {limitReached && !finished && (
        <p className="muted">Nombre maximal de messages atteint pour cette session.</p>
      )}
      {!speech.supported && canWrite && (
        <p className="notice">Dictée indisponible dans ce navigateur (utilise Chrome ou Edge) : tape ton message.</p>
      )}
      {speech.error && <p className="notice notice-error">{speech.error}</p>}
      <textarea
        aria-label="Ton message"
        className="sd-input"
        rows={3}
        maxLength={MAX_MESSAGE_CHARS}
        placeholder="Pose une question de clarification, énonce une hypothèse…"
        value={text}
        disabled={!canWrite || busy}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            if (text.trim() && canWrite && !busy) void submit();
          }
        }}
      />
      {speech.interim && <p className="muted composer-interim">{speech.interim}</p>}
      <div className="composer-actions">
        {speech.supported ? (
          <button
            type="button"
            className={`btn mic-btn${speech.listening ? " is-listening" : ""}`}
            aria-pressed={speech.listening}
            disabled={!canWrite || busy}
            onClick={speech.listening ? speech.stop : speech.start}
          >
            {speech.listening ? "Arrêter la dictée" : "Dicter"}
          </button>
        ) : (
          <span />
        )}
        <button
          type="button"
          className="btn btn-primary"
          disabled={!canWrite || busy || text.trim().length === 0}
          onClick={() => void submit()}
        >
          Envoyer
        </button>
      </div>
    </section>
  );
}
