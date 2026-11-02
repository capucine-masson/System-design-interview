import { formatDuration } from "../managerLabels";
import type { Turn } from "../types";

export default function Conversation({ turns }: { turns: Turn[] }) {
  if (turns.length === 0) return null;
  return (
    <ol className="conversation" aria-label="Échanges">
      {turns.map((turn) => (
        <li key={`${turn.kind}-${turn.created_at}`} className={`turn turn-${turn.kind}`}>
          <p className="turn-author muted">
            {turn.kind === "answer"
              ? `Toi${turn.duree_s ? ` · ${formatDuration(turn.duree_s)}` : ""}`
              : "Le manager"}
          </p>
          <p className="turn-text">{turn.texte}</p>
        </li>
      ))}
    </ol>
  );
}
