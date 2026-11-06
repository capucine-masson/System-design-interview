import { useState } from "react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useI18n } from "../i18n";
import { MAX_ANSWER_CHARS } from "../managerLabels";

interface VoiceAnswerProps {
  busy: boolean;
  /** Envoie la réponse ; retourne true si la correction a abouti. */
  onSubmit: (text: string) => Promise<boolean>;
}

/** Micro centré (dictée du navigateur) + zone de texte éditable, aussi utilisable sans micro. */
export default function VoiceAnswer({ busy, onSubmit }: VoiceAnswerProps) {
  const { t } = useI18n();
  const [text, setText] = useState("");
  const speech = useSpeechRecognition((finalText) =>
    setText((current) => (current ? `${current} ${finalText}` : finalText)),
  );

  const submit = async (): Promise<void> => {
    speech.stop();
    await onSubmit(text.trim());
  };

  return (
    <div className="voice-answer">
      {!speech.supported && <p className="notice">{t("composer.noSpeech")}</p>}
      {speech.error && <p className="notice notice-error">{speech.error}</p>}
      <div className="voice-field">
        <textarea
          className="composer-text"
          aria-label={t("composer.textLabel")}
          placeholder={t("composer.placeholder")}
          maxLength={MAX_ANSWER_CHARS}
          value={text}
          disabled={busy}
          onChange={(event) => setText(event.target.value)}
        />
        {speech.listening && (
          <p className="voice-live" aria-live="polite">
            <span className="voice-dot" aria-hidden="true" />
            <span className="voice-live-text">{speech.interim || t("revision.listening")}</span>
          </p>
        )}
      </div>
      <div className="voice-actions">
        {speech.supported ? (
          <button
            type="button"
            className={`btn mic-btn${speech.listening ? " is-listening" : ""}`}
            aria-pressed={speech.listening}
            disabled={busy}
            onClick={speech.listening ? speech.stop : speech.start}
          >
            {speech.listening ? t("composer.stopDictation") : t("composer.dictate")}
          </button>
        ) : (
          <span />
        )}
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy || text.trim().length === 0}
          onClick={() => void submit()}
        >
          {busy ? t("revision.reviewing") : t("revision.send")}
        </button>
      </div>
    </div>
  );
}
