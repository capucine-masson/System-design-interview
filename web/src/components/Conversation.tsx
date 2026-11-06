import { useI18n } from "../i18n";
import { formatDuration } from "../managerLabels";
import type { Turn } from "../types";

export default function Conversation({ turns }: { turns: Turn[] }) {
  const { t } = useI18n();
  if (turns.length === 0) return null;
  return (
    <ol className="conversation" aria-label={t("manager.conversation")}>
      {turns.map((turn) => (
        <li key={`${turn.kind}-${turn.created_at}`} className={`turn turn-${turn.kind}`}>
          <p className="turn-author muted">
            {turn.kind === "answer"
              ? `${t("common.you")}${turn.duree_s ? ` · ${formatDuration(turn.duree_s)}` : ""}`
              : t("manager.managerAuthor")}
          </p>
          <p className="turn-text">{turn.texte}</p>
        </li>
      ))}
    </ol>
  );
}
