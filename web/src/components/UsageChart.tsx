import { useI18n } from "../i18n";
import type { UsagePoint } from "../types";

const SIZE = 100;
const MIN_POINTS = 2;
const GRID_LINES = [0, SIZE / 2, SIZE];

/** Courbe des tokens consommés par appel, du plus ancien au plus récent. */
export default function UsageChart({ points }: { points: UsagePoint[] }) {
  const { t, locale } = useI18n();
  if (points.length < MIN_POINTS) {
    return <p className="muted">{t("usage.chartNeedTwo")}</p>;
  }
  const max = Math.max(...points.map((p) => p.tokens), 1);
  const x = (index: number): number => (index * SIZE) / (points.length - 1);
  const y = (tokens: number): number => SIZE - (tokens * SIZE) / max;
  const line = points.map((p, i) => `${x(i)},${y(p.tokens)}`).join(" ");
  const format = (value: number): string => Math.round(value).toLocaleString(locale);
  const formatDate = (iso: string): string =>
    new Date(iso).toLocaleString(locale, { dateStyle: "short", timeStyle: "short" });
  return (
    <div className="usage-chart" role="img" aria-label={t("usage.chartAria")}>
      <div className="usage-chart-y">
        <span>{format(max)}</span>
        <span>{format(max / 2)}</span>
        <span>0</span>
      </div>
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} preserveAspectRatio="none" className="usage-chart-plot">
        {GRID_LINES.map((value) => (
          <line key={value} x1={0} x2={SIZE} y1={value} y2={value} className="usage-chart-grid" />
        ))}
        <polygon points={`0,${SIZE} ${line} ${SIZE},${SIZE}`} className="usage-chart-area" />
        <polyline points={line} className="usage-chart-line" />
      </svg>
      <div className="usage-chart-x">
        <span>{formatDate(points[0].at)}</span>
        <span>{formatDate(points[points.length - 1].at)}</span>
      </div>
    </div>
  );
}
