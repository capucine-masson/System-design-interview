import { useState } from "react";

interface SdFinishProps {
  finished: boolean;
  busy: boolean;
  onFinish: () => Promise<void>;
}

export default function SdFinish({ finished, busy, onFinish }: SdFinishProps) {
  const [confirming, setConfirming] = useState(false);

  if (finished) {
    return (
      <p className="notice" role="status">
        Session terminée. La correction détaillée arrivera à l&apos;étape suivante ; ton schéma et ta
        discussion sont conservés.
      </p>
    );
  }
  if (!confirming) {
    return (
      <button type="button" className="btn btn-primary" onClick={() => setConfirming(true)}>
        Terminer et obtenir la correction
      </button>
    );
  }
  return (
    <div className="notice" role="alertdialog" aria-label="Confirmer la fin de la session">
      <p>Terminer la session ? Tu ne pourras plus écrire ni modifier le schéma.</p>
      <div className="setup-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy}
          onClick={() => void onFinish()}
        >
          Oui, terminer
        </button>
        <button type="button" className="btn" disabled={busy} onClick={() => setConfirming(false)}>
          Annuler
        </button>
      </div>
    </div>
  );
}
