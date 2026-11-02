import { MAX_NOTE } from "../managerLabels";
import type { CorrectionBundle, SdNotes } from "../types";
import Diagram from "./Diagram";

const DECIMALS = 1;

const CRITERIA: { key: keyof SdNotes; label: string }[] = [
  { key: "clarification", label: "Clarification du besoin" },
  { key: "hypotheses", label: "Hypothèses" },
  { key: "architecture", label: "Architecture et schéma" },
  { key: "approfondissement", label: "Approfondissement (zoom)" },
  { key: "compromis", label: "Compromis" },
  { key: "evaluation_monitoring", label: "Évaluation et monitoring" },
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
  const { correction, reference, details } = bundle;
  const missed = details.filter((d) => !d.decouvert);
  return (
    <section className="correction" aria-label="Correction">
      <div className="card feedback">
        <div className="page-head">
          <h2>Correction</h2>
          <p className="feedback-average">
            {bundle.moyenne.toFixed(DECIMALS)} <span className="muted">/ {MAX_NOTE}</span>
          </p>
        </div>
        <p>{correction.resume}</p>
        <ul className="notes">
          {CRITERIA.map((criterion) => (
            <li key={criterion.key}>
              <span>{criterion.label}</span>
              <progress max={MAX_NOTE} value={correction.notes[criterion.key]} />
              <strong>
                {correction.notes[criterion.key]}/{MAX_NOTE}
              </strong>
            </li>
          ))}
        </ul>
        <div className="feedback-lists">
          <Bullets title="Points forts" items={correction.points_forts} />
          <Bullets title="Points faibles" items={correction.points_faibles} />
          <Bullets title="Composants manquants dans ton schéma" items={correction.composants_manquants} />
        </div>
        <h3>Pour la prochaine fois</h3>
        <ol>
          {correction.conseils.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ol>
      </div>

      <div className="card">
        <h3>Ce que l&apos;interviewer te cachait</h3>
        <p className="muted">
          {missed.length === 0
            ? "Tu as obtenu tous les détails : bien joué."
            : `${missed.length} détail${missed.length > 1 ? "s" : ""} sur ${details.length} n'${
                missed.length > 1 ? "ont" : "a"
              } pas été demandé${missed.length > 1 ? "s" : ""}.`}
        </p>
        <ul className="hidden-details">
          {details.map((d) => (
            <li key={d.sujet} className={d.decouvert ? "is-found" : "is-missed"}>
              <span className="hidden-status">{d.decouvert ? "Obtenu" : "Non demandé"}</span>
              <strong>{d.sujet}</strong> : {d.valeur}
            </li>
          ))}
        </ul>
      </div>

      <div className="card reference">
        <h3>Solution de référence</h3>
        {reference.diagramme && <Diagram diagram={reference.diagramme} />}
        <div className="feedback-lists">
          <Bullets title="Hypothèses" items={reference.hypotheses} />
          <Bullets title="Dimensionnement" items={reference.dimensionnement} />
        </div>
        <h4>Composants</h4>
        <ul>
          {reference.composants.map((c) => (
            <li key={c.nom}>
              <strong>{c.nom}</strong> : {c.role}
            </li>
          ))}
        </ul>
        <h4>Parcours principal</h4>
        <ol>
          {reference.flux.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <h4>Compromis</h4>
        <ul>
          {reference.compromis.map((t) => (
            <li key={t.choix}>
              <strong>{t.choix}</strong> plutôt que {t.alternative} : {t.raison}
            </li>
          ))}
        </ul>
        <div className="feedback-lists">
          <Bullets title="Évaluation et monitoring" items={reference.evaluation_monitoring} />
          <Bullets title="Pièges fréquents" items={reference.pieges} />
        </div>
      </div>
    </section>
  );
}
