import { useEffect, useState } from "react";
import { getUsage } from "../api";
import EmptyState from "../components/EmptyState";
import type { UsageSummary } from "../types";

const COST_DECIMALS = 4;
const formatNumber = (value: number): string => value.toLocaleString("fr-FR");
const formatCost = (value: number): string =>
  value.toLocaleString("fr-FR", { minimumFractionDigits: COST_DECIMALS });

export default function Consommation() {
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getUsage()
      .then(setUsage)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section>
      <h1>Consommation API</h1>
      {error && <div className="card error">{error}</div>}
      {!error && !usage && <p className="muted">Chargement…</p>}
      {usage && usage.total.calls === 0 && (
        <EmptyState title="Aucun appel IA" hint="Aucune consommation enregistrée pour l'instant." />
      )}
      {usage && usage.total.calls > 0 && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Fonctionnalité</th>
                <th>Appels</th>
                <th>Tokens entrée</th>
                <th>Tokens sortie</th>
                <th>Coût estimé</th>
              </tr>
            </thead>
            <tbody>
              {[...usage.by_feature, usage.total].map((row) => (
                <tr key={row.feature} className={row === usage.total ? "total" : undefined}>
                  <td>{row.feature}</td>
                  <td>{formatNumber(row.calls)}</td>
                  <td>{formatNumber(row.tokens_in)}</td>
                  <td>{formatNumber(row.tokens_out)}</td>
                  <td>{formatCost(row.cost_estimate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
