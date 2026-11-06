import { useI18n } from "../i18n";
import type { CourseReview } from "../types";

type BlockKind = "right" | "mistakes" | "missing" | "details";

interface BlockProps {
  kind: BlockKind;
  title: string;
  items: string[];
}

function Block({ kind, title, items }: BlockProps) {
  if (items.length === 0) return null;
  return (
    <div className={`review-block review-block-${kind}`}>
      <h4 className="review-title">{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

/** Correction IA : verdict et réponse en 30 s en haut, puis le détail (erreurs, oublis, à savoir). */
export default function CourseReviewView({ review }: { review: CourseReview }) {
  const { t } = useI18n();
  return (
    <section className="review" aria-label={t("revision.correction")}>
      <div className={`review-main review-main-${review.verdict}`}>
        <h4 className="review-title">
          {t("revision.simple")}
          <span className={`verdict verdict-${review.verdict}`}>{t(`revision.verdict.${review.verdict}`)}</span>
        </h4>
        <p>{review.explication_simple}</p>
      </div>
      <div className="review-grid">
        <Block kind="mistakes" title={t("revision.mistakes")} items={review.erreurs} />
        <Block kind="missing" title={t("revision.missing")} items={review.points_manquants} />
        <Block kind="details" title={t("revision.details")} items={review.details} />
        <Block kind="right" title={t("revision.right")} items={review.points_justes} />
      </div>
    </section>
  );
}
