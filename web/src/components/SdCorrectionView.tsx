import { type TKey, useI18n } from "../i18n";
import { MAX_NOTE } from "../managerLabels";
import type { CorrectionBundle, SdNotes } from "../types";
import Diagram from "./Diagram";

const DECIMALS = 1;

const CRITERIA: { key: keyof SdNotes; label: TKey }[] = [
  { key: "clarification", label: "correction.clarification" },
  { key: "hypotheses", label: "correction.hypotheses" },
  { key: "architecture", label: "correction.architecture" },
  { key: "approfondissement", label: "correction.approfondissement" },
  { key: "compromis", label: "correction.compromis" },
  { key: "evaluation_monitoring", label: "correction.evaluation_monitoring" },
];

function Bullets({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function SdCorrectionView({ bundle }: { bundle: CorrectionBundle }) {
  const { t } = useI18n();
  const { correction, reference, details } = bundle;
  const missed = details.filter((d) => !d.decouvert);
  return (
    <section className="correction" aria-label={t("correction.aria")}>
      <div className="card feedback">
        <div className="page-head">
          <h2>{t("correction.title")}</h2>
          <p className="feedback-average">
            {bundle.moyenne.toFixed(DECIMALS)} <span className="muted">/ {MAX_NOTE}</span>
          </p>
        </div>
        <p>{correction.resume}</p>
        <ul className="notes">
          {CRITERIA.map((criterion) => (
            <li key={criterion.key}>
              <span>{t(criterion.label)}</span>
              <progress max={MAX_NOTE} value={correction.notes[criterion.key]} />
              <strong>
                {correction.notes[criterion.key]}/{MAX_NOTE}
              </strong>
            </li>
          ))}
        </ul>
        <div className="feedback-lists">
          <Bullets title={t("feedback.strengths")} items={correction.points_forts} />
          <Bullets title={t("feedback.weaknesses")} items={correction.points_faibles} />
          <Bullets
            title={t("correction.missingComponents")}
            items={correction.composants_manquants}
          />
        </div>
        <h3>{t("feedback.nextTime")}</h3>
        <ol>
          {correction.conseils.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ol>
      </div>

      <div className="card">
        <h3>{t("correction.hidden")}</h3>
        <p className="muted">
          {missed.length === 0
            ? t("correction.allFound")
            : t(missed.length > 1 ? "correction.missedMany" : "correction.missedOne", {
                missed: missed.length,
                total: details.length,
              })}
        </p>
        <ul className="hidden-details">
          {details.map((d) => (
            <li key={d.sujet} className={d.decouvert ? "is-found" : "is-missed"}>
              <span className="hidden-status">{d.decouvert ? t("correction.found") : t("correction.notAsked")}</span>
              <strong>{d.sujet}</strong> : {d.valeur}
            </li>
          ))}
        </ul>
      </div>

      <div className="card reference">
        <h3>{t("correction.reference")}</h3>
        {reference.diagramme && <Diagram diagram={reference.diagramme} />}
        <div className="feedback-lists">
          <Bullets title={t("correction.hypotheses")} items={reference.hypotheses} />
          <Bullets title={t("correction.sizing")} items={reference.dimensionnement} />
        </div>
        <h4>{t("correction.components")}</h4>
        <ul>
          {reference.composants.map((c) => (
            <li key={c.nom}>
              <strong>{c.nom}</strong> : {c.role}
            </li>
          ))}
        </ul>
        <h4>{t("correction.flow")}</h4>
        <ol>
          {reference.flux.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <h4>{t("correction.compromis")}</h4>
        <ul>
          {reference.compromis.map((tradeoff) => (
            <li key={tradeoff.choix}>
              <strong>{tradeoff.choix}</strong> {t("correction.rather")} {tradeoff.alternative} :{" "}
              {tradeoff.raison}
            </li>
          ))}
        </ul>
        <div className="feedback-lists">
          <Bullets
            title={t("correction.evaluation_monitoring")}
            items={reference.evaluation_monitoring}
          />
          <Bullets title={t("correction.pitfalls")} items={reference.pieges} />
        </div>
      </div>
    </section>
  );
}
