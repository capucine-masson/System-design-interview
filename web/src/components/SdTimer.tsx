import { useI18n } from "../i18n";
import { formatDuration } from "../managerLabels";
import { currentPhaseIndex, PHASES, SESSION_MINUTES, SESSION_SECONDS } from "../sdPhases";

/** Minuteur de 45 minutes : indicatif, il ne bloque jamais la session. */
export default function SdTimer({ elapsed }: { elapsed: number }) {
  const { t } = useI18n();
  const remaining = SESSION_SECONDS - elapsed;
  const over = remaining < 0;
  const current = currentPhaseIndex(elapsed);
  return (
    <section className="sd-timer card" aria-label={t("timer.aria")}>
      <div className="sd-timer-clock">
        <span className={`timer${over ? " timer-over" : ""}`} role="timer" aria-label={t("timer.remaining")}>
          {over ? `+${formatDuration(-remaining)}` : formatDuration(remaining)}
        </span>
        <span className="muted">
          {over ? t("timer.over") : t("timer.left", { min: SESSION_MINUTES })}
        </span>
      </div>
      <ol className="phases" aria-label={t("timer.phases")}>
        {PHASES.map((phase, index) => (
          <li
            key={phase.label}
            className={`phase${index === current ? " is-current" : ""}${index < current ? " is-past" : ""}`}
            aria-current={index === current ? "step" : undefined}
            title={t("timer.from", { min: phase.startMinute })}
          >
            {t(phase.label)}
          </li>
        ))}
      </ol>
    </section>
  );
}
