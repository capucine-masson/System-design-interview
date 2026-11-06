import { Link } from "react-router-dom";
import { useI18n } from "../i18n";
import type { Theme } from "../types";
import ProgressBar from "./ProgressBar";
import StatusIcon from "./StatusIcon";

interface ThemeTileProps {
  theme: Theme;
  to: string;
  pending: boolean;
  onToggle: (theme: Theme) => void;
}

/** Card d'un thème : rond à cocher (« je maîtrise ») + lien vers ses cartes + progression. */
export default function ThemeTile({ theme, to, pending, onToggle }: ThemeTileProps) {
  const { t } = useI18n();
  const label = theme.fait ? t("theme.unmark") : t("theme.mark");
  return (
    <div className={`card theme-card${theme.fait ? " done" : ""}`}>
      <div className="theme-head">
        <button
          type="button"
          className="theme-check"
          aria-pressed={theme.fait}
          aria-label={label}
          title={label}
          disabled={pending}
          onClick={() => onToggle(theme)}
        >
          <StatusIcon statut={theme.fait ? "maitrisee" : null} />
        </button>
        <Link to={to} className="theme-link">
          <h2>{theme.titre}</h2>
        </Link>
      </div>
      <ProgressBar maitrisees={theme.maitrisees} aRevoir={theme.a_revoir} total={theme.total} />
    </div>
  );
}
