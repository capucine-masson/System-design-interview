import { useI18n } from "../i18n";

interface ProgressBarProps {
  maitrisees: number;
  aRevoir: number;
  total: number;
}

const PERCENT = 100;

export default function ProgressBar({ maitrisees, aRevoir, total }: ProgressBarProps) {
  const { t } = useI18n();
  const percent = total === 0 ? 0 : Math.round((maitrisees / total) * PERCENT);
  return (
    <div className="progress">
      <div
        className="progress-track"
        role="progressbar"
        aria-label={t("progress.barLabel")}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={maitrisees}
      >
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <p className="progress-text muted">
        {t("progress.text", { mastered: maitrisees, total, toReview: aRevoir })}
      </p>
    </div>
  );
}
