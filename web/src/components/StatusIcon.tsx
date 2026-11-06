import { useI18n } from "../i18n";
import type { Statut } from "../types";

interface StatusIconProps {
  statut: Statut | null;
}

/** Pastille de suivi : coche pleine (maîtrisée), flèche (à revoir) ou cercle vide. */
export default function StatusIcon({ statut }: StatusIconProps) {
  const { t } = useI18n();
  const label =
    statut === "maitrisee"
      ? t("progress.mastered")
      : statut === "a_revoir"
        ? t("progress.toReview")
        : t("card.notMarked");
  return (
    <svg
      className={`status-icon status-${statut ?? "none"}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <title>{label}</title>
      <circle cx="12" cy="12" r="9.5" />
      {statut === "maitrisee" && <path d="M7.5 12.5l3 3 6-6.5" />}
      {statut === "a_revoir" && <path d="M16 9.5A5 5 0 1 0 17 13M16 6v3.5h-3.5" />}
    </svg>
  );
}
