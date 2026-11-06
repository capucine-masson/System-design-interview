import { useI18n } from "../i18n";
import { CRITERIA, MAX_NOTE } from "../managerLabels";
import type { Feedback, ReponseOrale } from "../types";

const DECIMALS = 1;

function SpokenBlock({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="spoken-block">
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function SpokenAnswer({ answer }: { answer: ReponseOrale }) {
  const { t } = useI18n();
  return (
    <div className="spoken">
      <div className="spoken-block spoken-decision">
        <h4>{t("feedback.myDecision")}</h4>
        <p>{answer.decision}</p>
      </div>
      <SpokenBlock title={t("feedback.myActions")} items={answer.actions} />
      <SpokenBlock title={t("feedback.tradeoff")} items={answer.compromis} />
      <SpokenBlock title={t("feedback.stakeholders")} items={answer.parties_prenantes} />
    </div>
  );
}

function Bullets({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default function FeedbackView({ feedback }: { feedback: Feedback }) {
  const { t } = useI18n();
  const values = CRITERIA.map((criterion) => feedback.notes[criterion.key]);
  const average = values.reduce((sum, value) => sum + value, 0) / values.length;
  return (
    <section className="card feedback" aria-label={t("feedback.title")}>
      <div className="page-head">
        <h2>{t("feedback.title")}</h2>
        <p className="feedback-average">
          {average.toFixed(DECIMALS)} <span className="muted">/ {MAX_NOTE}</span>
        </p>
      </div>
      <ul className="notes">
        {CRITERIA.map((criterion) => (
          <li key={criterion.key}>
            <span>{t(criterion.label)}</span>
            <progress max={MAX_NOTE} value={feedback.notes[criterion.key]} />
            <strong>
              {feedback.notes[criterion.key]}/{MAX_NOTE}
            </strong>
          </li>
        ))}
      </ul>
      <div className="feedback-lists">
        <Bullets title={t("feedback.strengths")} items={feedback.points_forts} />
        <Bullets title={t("feedback.weaknesses")} items={feedback.points_faibles} />
        <Bullets title={t("feedback.omissions")} items={feedback.oublis} />
      </div>
      <h3>{t("feedback.improved")}</h3>
      <SpokenAnswer answer={feedback.reponse_amelioree} />
      <h3>{t("feedback.nextTime")}</h3>
      <ol>
        {feedback.conseils.map((tip) => (
          <li key={tip}>{tip}</li>
        ))}
      </ol>
    </section>
  );
}
