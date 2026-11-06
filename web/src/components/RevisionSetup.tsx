import { useI18n } from "../i18n";
import StarIcon from "./StarIcon";
import type { RevisionCount } from "../types";

interface RevisionSetupProps {
  available: number;
  count: RevisionCount;
  onlyToReview: boolean;
  onlyEssential: boolean;
  loading: boolean;
  onCount: (count: RevisionCount) => void;
  onToggleToReview: () => void;
  onToggleEssential: () => void;
  onStart: () => void;
}

const FIXED_COUNTS = [5, 10] as const;

/** Choix du nombre de cartes (5, 10, max) et du filtre « à revoir » avant de commencer. */
export default function RevisionSetup(props: RevisionSetupProps) {
  const { t } = useI18n();
  const { available, count, onlyToReview, onlyEssential, loading } = props;
  return (
    <div className="card revision-setup">
      <h2>{t("revision.howMany")}</h2>
      <div className="toolbar" role="group" aria-label={t("revision.howMany")}>
        {FIXED_COUNTS.map((n) => (
          <button
            key={n}
            type="button"
            className="btn"
            aria-pressed={count === n}
            onClick={() => props.onCount(n)}
          >
            {n}
          </button>
        ))}
        <button type="button" className="btn" aria-pressed={count === "max"} onClick={() => props.onCount("max")}>
          {t("revision.countMax", { n: available })}
        </button>
      </div>
      <div className="revision-filters">
        <button type="button" className="btn" aria-pressed={onlyToReview} onClick={props.onToggleToReview}>
          {onlyToReview ? t("revision.allCards") : t("revision.onlyToReview")}
        </button>
        <label className="check">
          <input type="checkbox" checked={onlyEssential} onChange={props.onToggleEssential} />
          <span>{t("revision.onlyEssential")}</span>
          <StarIcon className="check-star" />
        </label>
      </div>
      <div className="revision-footer">
        <p className="muted">{t("revision.available", { n: available })}</p>
        <button type="button" className="btn btn-primary" disabled={loading || available === 0} onClick={props.onStart}>
          {loading ? t("common.drawing") : t("revision.start")}
        </button>
      </div>
    </div>
  );
}
