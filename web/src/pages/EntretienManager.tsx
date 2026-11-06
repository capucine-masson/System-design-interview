import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createSession, drawQuestion, generateQuestion, listQuestions } from "../api";
import { useI18n } from "../i18n";
import { categorieLabel, CATEGORIES, difficulteLabel, DIFFICULTES } from "../managerLabels";
import type { Categorie, Difficulte, Question } from "../types";

type Action = "generate" | "draw";

export default function EntretienManager() {
  const { lang, t } = useI18n();
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
  }, [categorie, difficulte, lang]);

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
      setError(err instanceof Error ? err.message : t("manager.startFailed"));
      setBusy(null);
    }
  };

  const disabled = busy !== null;
  return (
    <section>
      <div className="page-head">
        <h1>{t("manager.title")}</h1>
        <Link to="/historique" className="btn">
          {t("manager.viewHistory")}
        </Link>
      </div>
      <div className="card setup">
        <p className="muted">{t("manager.intro")}</p>
        <div className="setup-fields">
          <label>
            {t("manager.category")}
            <select
              value={categorie}
              disabled={disabled}
              onChange={(event) => setCategorie(event.target.value as Categorie)}
            >
              {CATEGORIES.map((value) => (
                <option key={value} value={value}>
                  {categorieLabel(value, t)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("manager.difficulty")}
            <select
              value={difficulte}
              disabled={disabled}
              onChange={(event) => setDifficulte(event.target.value as Difficulte)}
            >
              {DIFFICULTES.map((value) => (
                <option key={value} value={value}>
                  {difficulteLabel(value, t)}
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
            {busy === "generate" ? t("manager.generating") : t("manager.generate")}
          </button>
          <button
            type="button"
            className="btn"
            disabled={disabled || bankSize === 0}
            onClick={() => void start("draw")}
          >
            {busy === "draw" ? t("common.drawing") : t("common.draw")}
          </button>
        </div>
        <p className="muted">
          {bankSize === null
            ? t("manager.bankLoading")
            : t(bankSize > 1 ? "manager.bankMany" : "manager.bankOne", { n: bankSize })}
        </p>
        {error && <div className="notice notice-error">{error}</div>}
      </div>
    </section>
  );
}
