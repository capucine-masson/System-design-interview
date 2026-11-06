import { useI18n } from "../i18n";
import { MAX_NOTE } from "../managerLabels";
import type { SessionSummary } from "../types";

const WIDTH = 600;
const HEIGHT = 180;
const PAD_X = 32;
const PAD_Y = 20;
const MIN_POINTS = 2;
const MIN_NOTE = 1;

/** Évolution de la moyenne des notes, de la plus ancienne session à la plus récente. */
export default function ScoreChart({ sessions }: { sessions: SessionSummary[] }) {
  const { t } = useI18n();
  const scored = sessions
    .filter((s) => s.moyenne !== null)
    .sort((a, b) => a.id - b.id);
  if (scored.length < MIN_POINTS) {
    return <p className="muted">{t("chart.needTwo")}</p>;
  }
  const x = (index: number): number =>
    PAD_X + (index * (WIDTH - 2 * PAD_X)) / (scored.length - 1);
  const y = (value: number): number =>
    HEIGHT - PAD_Y - ((value - MIN_NOTE) * (HEIGHT - 2 * PAD_Y)) / (MAX_NOTE - MIN_NOTE);
  const points = scored.map((s, i) => `${x(i)},${y(s.moyenne ?? MIN_NOTE)}`).join(" ");
  const grid = Array.from({ length: MAX_NOTE - MIN_NOTE + 1 }, (_, i) => MIN_NOTE + i);
  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="chart"
      role="img"
      aria-label={t("chart.aria")}
    >
      {grid.map((value) => (
        <g key={value}>
          <line x1={PAD_X} x2={WIDTH - PAD_X} y1={y(value)} y2={y(value)} className="chart-grid" />
          <text x={PAD_X - 8} y={y(value)} textAnchor="end" dominantBaseline="central" className="chart-label">
            {value}
          </text>
        </g>
      ))}
      <polyline points={points} className="chart-line" />
      {scored.map((s, i) => (
        <circle key={s.id} cx={x(i)} cy={y(s.moyenne ?? MIN_NOTE)} r={4} className="chart-dot">
          <title>{t("chart.point", { id: s.id, average: s.moyenne ?? MIN_NOTE, max: MAX_NOTE })}</title>
        </circle>
      ))}
    </svg>
  );
}
