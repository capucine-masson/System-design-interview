import { formatDuration } from "../managerLabels";
import { currentPhaseIndex, PHASES, SESSION_MINUTES, SESSION_SECONDS } from "../sdPhases";

/** Minuteur de 45 minutes : indicatif, il ne bloque jamais la session. */
export default function SdTimer({ elapsed }: { elapsed: number }) {
  const remaining = SESSION_SECONDS - elapsed;
  const over = remaining < 0;
  const current = currentPhaseIndex(elapsed);
  return (
    <section className="sd-timer card" aria-label="Minuteur et étapes conseillées">
      <div className="sd-timer-clock">
        <span className={`timer${over ? " timer-over" : ""}`} role="timer" aria-label="Temps restant">
          {over ? `+${formatDuration(-remaining)}` : formatDuration(remaining)}
        </span>
        <span className="muted">
          {over ? "temps dépassé" : `restant sur ${SESSION_MINUTES} min`}
        </span>
      </div>
      <ol className="phases" aria-label="Étapes conseillées">
        {PHASES.map((phase, index) => (
          <li
            key={phase.label}
            className={`phase${index === current ? " is-current" : ""}${index < current ? " is-past" : ""}`}
            aria-current={index === current ? "step" : undefined}
            title={`À partir de ${phase.startMinute} min`}
          >
            {phase.label}
          </li>
        ))}
      </ol>
    </section>
  );
}
