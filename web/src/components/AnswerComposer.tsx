import { useEffect, useState } from "react";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useI18n } from "../i18n";
import { formatDuration, MAX_ANSWER_CHARS, TARGET_MAX_S, TARGET_MIN_S } from "../managerLabels";

interface AnswerComposerProps {
  busy: boolean;
  /** Retourne true si la réponse a bien été enregistrée (le champ est alors vidé). */
  onSubmit: (text: string, durationS: number) => Promise<boolean>;
}

const TICK_MS = 1000;

function timerClass(elapsed: number): string {
  if (elapsed < TARGET_MIN_S) return "timer";
  return elapsed <= TARGET_MAX_S ? "timer timer-ok" : "timer timer-over";
}

export default function AnswerComposer({ busy, onSubmit }: AnswerComposerProps) {
  const { t } = useI18n();
  const [text, setText] = useState("");
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const speech = useSpeechRecognition((finalText) =>
    setText((current) => (current ? `${current} ${finalText}` : finalText)),
  );

  useEffect(() => {
    if (startedAt === null) return;
    const id = window.setInterval(
      () => setElapsed(Math.floor((Date.now() - startedAt) / TICK_MS)),
      TICK_MS,
    );
    return () => window.clearInterval(id);
  }, [startedAt]);

  const markStarted = (): void => setStartedAt((current) => current ?? Date.now());

  const toggleMic = (): void => {
    if (speech.listening) {
      speech.stop();
      return;
    }
    markStarted();
    speech.start();
  };

  const submit = async (): Promise<void> => {
    speech.stop();
    const duration = startedAt === null ? 0 : Math.floor((Date.now() - startedAt) / TICK_MS);
    if (await onSubmit(text.trim(), duration)) {
      setText("");
      setStartedAt(null);
      setElapsed(0);
    }
  };

  return (
    <section className="card composer" aria-label={t("composer.aria")}>
      <div className="composer-bar">
        {speech.supported && (
          <button
            type="button"
            className={`btn mic-btn${speech.listening ? " is-listening" : ""}`}
            aria-pressed={speech.listening}
            disabled={busy}
            onClick={toggleMic}
          >
            {speech.listening ? t("composer.stopDictation") : t("composer.dictate")}
          </button>
        )}
        <span className={timerClass(elapsed)} role="timer" aria-label={t("composer.timer")}>
          {formatDuration(elapsed)}
        </span>
        <span className="muted">
          {t("composer.target", { min: formatDuration(TARGET_MIN_S), max: formatDuration(TARGET_MAX_S) })}
        </span>
      </div>
      {!speech.supported && (
        <p className="notice">{t("composer.noSpeech")}</p>
      )}
      {speech.error && <p className="notice notice-error">{speech.error}</p>}
      <textarea
        className="composer-text"
        aria-label={t("composer.textLabel")}
        placeholder={t("composer.placeholder")}
        rows={8}
        maxLength={MAX_ANSWER_CHARS}
        value={text}
        disabled={busy}
        onChange={(event) => {
          setText(event.target.value);
          if (event.target.value) markStarted();
        }}
      />
      {speech.interim && <p className="muted composer-interim">{speech.interim}</p>}
      <div className="composer-actions">
        <span className="muted">
          {text.length}/{MAX_ANSWER_CHARS}
        </span>
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy || text.trim().length === 0}
          onClick={() => void submit()}
        >
          {t("composer.send")}
        </button>
      </div>
    </section>
  );
}
