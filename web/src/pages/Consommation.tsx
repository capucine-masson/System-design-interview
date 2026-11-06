import { useEffect, useState } from "react";
import { getUsage } from "../api";
import EmptyState from "../components/EmptyState";
import UsageChart from "../components/UsageChart";
import { type TKey, useI18n } from "../i18n";
import type { GroupUsage, UsageSummary } from "../types";

const COST_DECIMALS = 4;
const CURRENCY = "€";

const GROUP_LABELS: Record<string, TKey> = {
  cours: "usage.group.cours",
  workflows: "usage.group.workflows",
  manager: "usage.group.manager",
  system_design: "usage.group.system_design",
  autre: "usage.group.autre",
};

const totalTokens = (usage: GroupUsage): number => usage.tokens_in + usage.tokens_out;

export default function Consommation() {
  const { t, locale } = useI18n();
  const formatNumber = (value: number): string => value.toLocaleString(locale);
  const formatCost = (value: number): string =>
    `${value.toLocaleString(locale, { minimumFractionDigits: COST_DECIMALS })} ${CURRENCY}`;
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getUsage()
      .then(setUsage)
      .catch((err: Error) => setError(err.message));
  }, []);

  const hasCalls = usage !== null && usage.total.calls > 0;
  return (
    <section className={hasCalls ? "usage-page" : undefined}>
      <h1>{t("usage.title")}</h1>
      {error && <div className="card error">{error}</div>}
      {!error && !usage && <p className="muted">{t("common.loading")}</p>}
      {usage && !hasCalls && <EmptyState title={t("usage.empty")} hint={t("usage.emptyHint")} />}
      {usage && hasCalls && (
        <>
          <div className="usage-metrics">
            <div className="card usage-metric">
              <span className="muted">{t("usage.totalTokens")}</span>
              <strong>{formatNumber(totalTokens(usage.total))}</strong>
            </div>
            <div className="card usage-metric">
              <span className="muted">{t("usage.totalCost")}</span>
              <strong>{formatCost(usage.total.cost_estimate)}</strong>
            </div>
            <div className="card usage-metric">
              <span className="muted">{t("usage.calls")}</span>
              <strong>{formatNumber(usage.total.calls)}</strong>
            </div>
          </div>
          <h2 className="usage-subtitle">{t("usage.byExercise")}</h2>
          <div className="usage-groups">
            {usage.by_group.map((group) => (
              <div key={group.group} className="card usage-group">
                <span className="usage-group-name">{t(GROUP_LABELS[group.group] ?? "usage.group.autre")}</span>
                <strong>{formatNumber(totalTokens(group))}</strong>
                <span className="muted">
                  {formatCost(group.cost_estimate)} · {formatNumber(group.calls)} {t("usage.calls").toLowerCase()}
                </span>
              </div>
            ))}
          </div>
          <div className="card usage-chart-card">
            <h2>{t("usage.chartTitle", { n: usage.timeline.length })}</h2>
            <UsageChart points={usage.timeline} />
          </div>
        </>
      )}
    </section>
  );
}
