import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useI18n } from "../i18n";
import type { Card, Statut } from "../types";
import Diagram from "./Diagram";
import ProgressButtons from "./ProgressButtons";
import StarIcon from "./StarIcon";

interface FlipCardProps {
  card: Card;
  pending: boolean;
  onProgress: (card: Card, statut: Statut | null) => void;
  /** « link » : simple bouton « Ouvrir la carte », sans vignette ni boutons de progression. */
  variant?: "tile" | "link";
}

export default function FlipCard({ card, pending, onProgress, variant = "tile" }: FlipCardProps) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent): void => {
      if (event.key === "Escape") setOpen(false);
    };
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const progress = (
    <ProgressButtons
      statut={card.statut}
      disabled={pending}
      onChange={(statut) => onProgress(card, statut)}
    />
  );

  return (
    <article className={variant === "tile" ? "flip-card" : undefined}>
      {variant === "tile" ? (
        <>
          <button type="button" className="flip-front" aria-haspopup="dialog" onClick={() => setOpen(true)}>
            <span className="flip-title">{card.titre}</span>
            {card.essentielle && <StarIcon className="flip-star" />}
            <span className="flip-hint">{t("card.open")}</span>
          </button>
          <div className="flip-actions">{progress}</div>
        </>
      ) : (
        <button type="button" className="btn" aria-haspopup="dialog" onClick={() => setOpen(true)}>
          {t("card.open")}
        </button>
      )}
      {open &&
        createPortal(
          <div className="modal-backdrop" onClick={() => setOpen(false)}>
            <div
              className="modal"
              role="dialog"
              aria-modal="true"
              aria-label={card.titre}
              onClick={(event) => event.stopPropagation()}
            >
              <h2>
                {card.titre}
                {card.essentielle && <StarIcon className="modal-star" />}
              </h2>
              <p className="flip-accroche">{card.accroche}</p>
              <ol className="flip-points">
                {card.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ol>
              {card.diagram && <Diagram diagram={card.diagram} />}
              <div className="flip-source muted">
                {t("common.source")}{" "}
                {card.source_url ? (
                  <a href={card.source_url} target="_blank" rel="noreferrer">
                    {card.source_label ?? card.source_url}
                  </a>
                ) : (
                  (card.source_label ?? t("card.sourceUnknown"))
                )}
              </div>
              <div className="modal-footer">
                {progress}
                <button type="button" className="btn" autoFocus onClick={() => setOpen(false)}>
                  {t("common.close")}
                </button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </article>
  );
}
