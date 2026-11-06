import { useEffect, useState } from "react";
import { getUsage } from "../api";
import EmptyState from "../components/EmptyState";
import { useI18n } from "../i18n";
import type { UsageSummary } from "../types";

const COST_DECIMALS = 4;

export default function Consommation() {
  const { t, locale } = useI18n();
  const formatNumber = (value: number): string => value.toLocaleString(locale);
  const formatCost = (value: number): string =>
    value.toLocaleString(locale, { minimumFractionDigits: COST_DECIMALS });
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getUsage()
      .then(setUsage)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section>
      <h1>{t("usage.title")}</h1>
      {error && <div className="card error">{error}</div>}
      {!error && !usage && <p className="muted">{t("common.loading")}</p>}
      {usage && usage.total.calls === 0 && (
        <EmptyState title={t("usage.empty")} hint={t("usage.emptyHint")} />
      )}
      {usage && usage.total.calls > 0 && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>{t("usage.feature")}</th>
                <th>{t("usage.calls")}</th>
                <th>{t("usage.tokensIn")}</th>
                <th>{t("usage.tokensOut")}</th>
                <th>{t("usage.cost")}</th>
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
