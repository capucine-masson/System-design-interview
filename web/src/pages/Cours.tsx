import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getThemes } from "../api";
import EmptyState from "../components/EmptyState";
import ProgressBar from "../components/ProgressBar";
import type { Theme } from "../types";

export default function Cours() {
  const [themes, setThemes] = useState<Theme[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getThemes()
      .then(setThemes)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section>
      <div className="page-head">
        <h1>Cours</h1>
        {themes && themes.length > 0 && (
          <Link to="/cours/revision" className="btn btn-primary">
            Révision aléatoire
          </Link>
        )}
      </div>
      {error && <div className="card error">{error}</div>}
      {!error && !themes && <p className="muted">Chargement…</p>}
      {themes && themes.length === 0 && (
        <EmptyState
          title="Aucun thème"
          hint="Le contenu n'est pas encore en base : lance « uv run python -m api.seed »."
        />
      )}
      {themes && themes.length > 0 && (
        <div className="grid themes-grid">
          {themes.map((theme) => (
            <Link key={theme.slug} to={`/cours/${theme.slug}`} className="card theme-card">
              <h2>{theme.titre}</h2>
              <ProgressBar
                maitrisees={theme.maitrisees}
                aRevoir={theme.a_revoir}
                total={theme.total}
              />
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
