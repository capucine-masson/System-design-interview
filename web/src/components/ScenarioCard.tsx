import { useI18n } from "../i18n";
import { categorieLabel, difficulteLabel } from "../managerLabels";
import type { Question } from "../types";

export default function ScenarioCard({ question }: { question: Question }) {
  const { t } = useI18n();
  return (
    <section className="card scenario" aria-label={t("manager.scenario")}>
      <p className="muted scenario-tags">
        {categorieLabel(question.categorie, t)} · {difficulteLabel(question.difficulte, t)}
      </p>
      <p>{question.contexte}</p>
      <ul className="scenario-constraints">
        {question.contraintes.map((constraint) => (
          <li key={constraint}>{constraint}</li>
        ))}
      </ul>
      <p>
        <strong>{t("manager.stake")}</strong> {question.enjeu}
      </p>
      <p className="scenario-question">{question.enonce}</p>
    </section>
  );
}
