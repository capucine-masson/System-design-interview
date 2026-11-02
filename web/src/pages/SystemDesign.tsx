import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createSdSession, drawCase, generateCase, listCaseTypes } from "../api";
import SdSessionList from "../components/SdSessionList";
import type { CaseType, SdCase } from "../types";

type Action = "generate" | "draw";
const RANDOM = "random";

export default function SystemDesign() {
  const navigate = useNavigate();
  const [types, setTypes] = useState<CaseType[] | null>(null);
  const [selected, setSelected] = useState<string>(RANDOM);
  const [busy, setBusy] = useState<Action | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCaseTypes()
      .then(setTypes)
      .catch((err: Error) => setError(err.message));
  }, []);

  const start = async (action: Action): Promise<void> => {
    if (!types) return;
    setBusy(action);
    setError(null);
    try {
      const slug =
        selected === RANDOM ? types[Math.floor(Math.random() * types.length)].slug : selected;
      const found: SdCase =
        action === "generate"
          ? await generateCase(slug)
          : await drawCase(selected === RANDOM ? undefined : slug);
      const session = await createSdSession(found.id);
      navigate(`/system-design/sessions/${session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Échec du démarrage de la session.");
      setBusy(null);
    }
  };

  const disabled = busy !== null || types === null;
  return (
    <section>
      <h1>System Design</h1>
      <div className="card setup">
        <p className="muted">
          Choisis un cas (ou laisse le hasard décider). Tu reçois un énoncé volontairement flou : à
          toi de poser les bonnes questions à l&apos;interviewer, puis de dessiner. L&apos;IA n&apos;est
          appelée que lorsque tu cliques sur « Générer » ou que tu envoies un message.
        </p>
        {!types && !error && <p className="muted">Chargement des cas…</p>}
        {types && (
          <fieldset className="case-types">
            <legend>Cas</legend>
            <label className={`case-type${selected === RANDOM ? " is-selected" : ""}`}>
              <input
                type="radio"
                name="case-type"
                checked={selected === RANDOM}
                disabled={disabled}
                onChange={() => setSelected(RANDOM)}
              />
              <strong>Au hasard</strong>
              <span className="muted">Un cas tiré parmi tous les types.</span>
            </label>
            {types.map((type) => (
              <label
                key={type.slug}
                className={`case-type${selected === type.slug ? " is-selected" : ""}`}
              >
                <input
                  type="radio"
                  name="case-type"
                  checked={selected === type.slug}
                  disabled={disabled}
                  onChange={() => setSelected(type.slug)}
                />
                <strong>{type.titre}</strong>
                <span className="muted">{type.description}</span>
              </label>
            ))}
          </fieldset>
        )}
        <div className="setup-actions">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() => void start("generate")}
          >
            {busy === "generate" ? "Génération du brief…" : "Générer un brief"}
          </button>
          <button type="button" className="btn" disabled={disabled} onClick={() => void start("draw")}>
            {busy === "draw" ? "Tirage…" : "Tirer de la banque (sans IA)"}
          </button>
        </div>
        {error && <div className="notice notice-error">{error}</div>}
      </div>
      <SdSessionList
        title="Reprendre une session"
        emptyHint="Tes sessions de System Design apparaîtront ici."
      />
    </section>
  );
}
