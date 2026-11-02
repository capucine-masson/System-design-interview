import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createSession, drawQuestion, generateQuestion, listQuestions } from "../api";
import { CATEGORIES, DIFFICULTES } from "../managerLabels";
import type { Categorie, Difficulte, Question } from "../types";

type Action = "generate" | "draw";

export default function EntretienManager() {
  const navigate = useNavigate();
  const [categorie, setCategorie] = useState<Categorie>("mixte");
  const [difficulte, setDifficulte] = useState<Difficulte>("moyenne");
  const [bankSize, setBankSize] = useState<number | null>(null);
  const [busy, setBusy] = useState<Action | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setBankSize(null);
    listQuestions({ categorie, difficulte })
      .then((questions) => setBankSize(questions.length))
      .catch((err: Error) => setError(err.message));
  }, [categorie, difficulte]);

  const start = async (action: Action): Promise<void> => {
    setBusy(action);
    setError(null);
    try {
      const question: Question =
        action === "generate"
          ? await generateQuestion(categorie, difficulte)
          : await drawQuestion({ categorie, difficulte });
      const session = await createSession(question.id);
      navigate(`/entretien-manager/sessions/${session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec du démarrage de l'entretien.");
      setBusy(null);
    }
  };

  const disabled = busy !== null;
  return (
    <section>
      <div className="page-head">
        <h1>Entretien manager</h1>
        <Link to="/historique" className="btn">
          Voir l&apos;historique
        </Link>
      </div>
      <div className="card setup">
        <p className="muted">
          Un scénario court, ta réponse à l&apos;oral, une ou deux relances, puis un retour noté.
          L&apos;IA n&apos;est appelée que lorsque tu cliques sur un bouton.
        </p>
        <div className="setup-fields">
          <label>
            Catégorie
            <select
              value={categorie}
              disabled={disabled}
              onChange={(event) => setCategorie(event.target.value as Categorie)}
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Difficulté
            <select
              value={difficulte}
              disabled={disabled}
              onChange={(event) => setDifficulte(event.target.value as Difficulte)}
            >
              {DIFFICULTES.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="setup-actions">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() => void start("generate")}
          >
            {busy === "generate" ? "Génération en cours…" : "Générer une question"}
          </button>
          <button
            type="button"
            className="btn"
            disabled={disabled || bankSize === 0}
            onClick={() => void start("draw")}
          >
            {busy === "draw" ? "Tirage…" : "Tirer de la banque (sans IA)"}
          </button>
        </div>
        <p className="muted">
          {bankSize === null
            ? "Chargement de la banque…"
            : `Banque : ${bankSize} question${bankSize > 1 ? "s" : ""} pour ce filtre.`}
        </p>
        {error && <div className="notice notice-error">{error}</div>}
      </div>
    </section>
  );
}
