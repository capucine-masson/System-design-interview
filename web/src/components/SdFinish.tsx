import { useState } from "react";
import { useI18n } from "../i18n";

interface SdFinishProps {
  finished: boolean;
  busy: boolean;
  onFinish: () => Promise<void>;
}

export default function SdFinish({ finished, busy, onFinish }: SdFinishProps) {
  const { t } = useI18n();
  const [confirming, setConfirming] = useState(false);

  if (finished) {
    return (
      <p className="notice" role="status">
        {t("finish.done")}
      </p>
    );
  }
  if (!confirming) {
    return (
      <button type="button" className="btn btn-primary" onClick={() => setConfirming(true)}>
        {t("finish.button")}
      </button>
    );
  }
  return (
    <div className="notice" role="alertdialog" aria-label={t("finish.confirmAria")}>
      <p>{t("finish.confirmText")}</p>
      <div className="setup-actions">
        <button
          type="button"
          className="btn btn-primary"
          disabled={busy}
          onClick={() => void onFinish()}
        >
          {t("finish.yes")}
        </button>
        <button type="button" className="btn" disabled={busy} onClick={() => setConfirming(false)}>
          {t("common.cancel")}
        </button>
      </div>
    </div>
  );
}
