import { useEffect, useRef, useState } from "react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useI18n } from "../i18n";
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
  const { t } = useI18n();
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
    <section className="card sd-chat" aria-label={t("chat.aria")}>
      <ol className="sd-messages" aria-live="polite">
        {session.messages.map((message) => (
          <li key={message.id} className={`msg msg-${message.role}`}>
            <p className="msg-author muted">{message.role === "user" ? t("common.you") : t("chat.interviewer")}</p>
            <p className="msg-text">{message.content}</p>
          </li>
        ))}
        {busy && (
          <li className="msg msg-assistant muted" role="status">
            {t("chat.thinking")}
          </li>
        )}
        <div ref={bottomRef} />
      </ol>
      {error && <div className="notice notice-error">{error}</div>}
      {session.awaiting_reply && !busy && !finished && (
        <button type="button" className="btn" onClick={onRetryReply}>
          {t("chat.retry")}
        </button>
      )}
      {finished && <p className="muted">{t("chat.closed")}</p>}
      {limitReached && !finished && (
        <p className="muted">{t("chat.limit")}</p>
      )}
      {!speech.supported && canWrite && (
        <p className="notice">{t("chat.noDictation")}</p>
      )}
      {speech.error && <p className="notice notice-error">{speech.error}</p>}
      <textarea
        aria-label={t("chat.messageLabel")}
        className="sd-input"
        rows={3}
        maxLength={MAX_MESSAGE_CHARS}
        placeholder={t("chat.placeholder")}
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
            {speech.listening ? t("composer.stopDictation") : t("chat.dictate")}
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
          {t("chat.send")}
        </button>
      </div>
    </section>
  );
}
