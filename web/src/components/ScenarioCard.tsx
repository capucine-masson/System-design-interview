import { categorieLabel, difficulteLabel } from "../managerLabels";
import type { Question } from "../types";

export default function ScenarioCard({ question }: { question: Question }) {
  return (
    <section className="card scenario" aria-label="Scénario">
      <p className="muted scenario-tags">
        {categorieLabel(question.categorie)} · {difficulteLabel(question.difficulte)}
      </p>
      <p>{question.contexte}</p>
      <ul className="scenario-constraints">
        {question.contraintes.map((constraint) => (
          <li key={constraint}>{constraint}</li>
        ))}
      </ul>
      <p>
        <strong>Enjeu :</strong> {question.enjeu}
      </p>
      <p className="scenario-question">{question.enonce}</p>
    </section>
  );
}
