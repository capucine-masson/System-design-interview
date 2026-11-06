import type { Diagram as DiagramData, DiagramEdge, DiagramNode } from "../types";

const BOX_W = 152;
const BOX_H = 48;
const GAP_X = 80;
const GAP_Y = 28;
const PAD = 12;
const WRAP_AT = 18;
const LINE_HEIGHT = 15;

const cellX = (col: number): number => PAD + col * (BOX_W + GAP_X);
const cellY = (row: number): number => PAD + row * (BOX_H + GAP_Y);

/** Coupe un libellé long en deux lignes, au plus proche du milieu. */
function wrapLabel(label: string): string[] {
  if (label.length <= WRAP_AT || !label.includes(" ")) return [label];
  const middle = label.length / 2;
  const spaces = [...label.matchAll(/ /g)].map((m) => m.index);
  const cut = spaces.reduce((best, i) => (Math.abs(i - middle) < Math.abs(best - middle) ? i : best));
  return [label.slice(0, cut), label.slice(cut + 1)];
}

interface Segment {
  path: string;
  labelX: number;
  labelY: number;
}

/** Calcule le tracé d'une flèche : droite entre colonnes, verticale dans une colonne, arc en retour. */
function route(source: DiagramNode, target: DiagramNode): Segment {
  const sx = cellX(source.col);
  const sy = cellY(source.row);
  const tx = cellX(target.col);
  const ty = cellY(target.row);
  if (target.col > source.col) {
    const x1 = sx + BOX_W;
    const y1 = sy + BOX_H / 2;
    return { path: `M${x1},${y1} L${tx},${ty + BOX_H / 2}`, labelX: (x1 + tx) / 2, labelY: (y1 + ty + BOX_H / 2) / 2 - 6 };
  }
  if (target.col === source.col) {
    const down = target.row > source.row;
    const y1 = down ? sy + BOX_H : sy;
    const y2 = down ? ty : ty + BOX_H;
    return { path: `M${sx + BOX_W / 2},${y1} L${tx + BOX_W / 2},${y2}`, labelX: sx + BOX_W / 2 + 6, labelY: (y1 + y2) / 2 };
  }
  const x1 = sx + BOX_W / 2;
  const x2 = tx + BOX_W / 2;
  const bottom = Math.max(sy, ty) + BOX_H;
  const depth = bottom + GAP_Y;
  return {
    path: `M${x1},${sy + BOX_H} C${x1},${depth} ${x2},${depth} ${x2},${ty + BOX_H}`,
    labelX: (x1 + x2) / 2,
    labelY: depth - 4,
  };
}

function Edge({ edge, nodes }: { edge: DiagramEdge; nodes: Map<string, DiagramNode> }) {
  const source = nodes.get(edge.source);
  const target = nodes.get(edge.target);
  if (!source || !target) return null;
  const { path, labelX, labelY } = route(source, target);
  return (
    <g>
      <path d={path} className="diagram-edge" markerEnd="url(#diagram-arrow)" />
      {edge.label && (
        <text x={labelX} y={labelY} textAnchor="middle" className="diagram-edge-label">
          {edge.label}
        </text>
      )}
    </g>
  );
}

function Box({ node }: { node: DiagramNode }) {
  const lines = wrapLabel(node.label);
  const x = cellX(node.col);
  const y = cellY(node.row);
  const firstLineY = y + BOX_H / 2 - ((lines.length - 1) * LINE_HEIGHT) / 2;
  return (
    <g>
      <rect x={x} y={y} width={BOX_W} height={BOX_H} rx={8} className="diagram-box" />
      <text x={x + BOX_W / 2} y={firstLineY} textAnchor="middle" dominantBaseline="central" className="diagram-text">
        {lines.map((line, i) => (
          <tspan key={line} x={x + BOX_W / 2} dy={i === 0 ? 0 : LINE_HEIGHT}>
            {line}
          </tspan>
        ))}
      </text>
    </g>
  );
}

export default function Diagram({ diagram }: { diagram: DiagramData }) {
  const nodes = new Map(diagram.nodes.map((node) => [node.id, node]));
  const hasLoop = diagram.edges.some((e) => {
    const s = nodes.get(e.source);
    const t = nodes.get(e.target);
    return s && t && t.col < s.col;
  });
  const cols = Math.max(...diagram.nodes.map((n) => n.col)) + 1;
  const rows = Math.max(...diagram.nodes.map((n) => n.row)) + 1;
  const width = PAD * 2 + cols * BOX_W + (cols - 1) * GAP_X;
  const height = PAD * 2 + rows * BOX_H + (rows - 1) * GAP_Y + (hasLoop ? GAP_Y : 0);
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="diagram"
      role="img"
      aria-label={`Schéma : ${diagram.nodes.map((n) => n.label).join(", ")}`}
    >
      <defs>
        <marker id="diagram-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" className="diagram-arrow" />
        </marker>
      </defs>
      {diagram.edges.map((edge) => (
        <Edge key={`${edge.source}-${edge.target}`} edge={edge} nodes={nodes} />
      ))}
      {diagram.nodes.map((node) => (
        <Box key={node.id} node={node} />
      ))}
    </svg>
  );
}
