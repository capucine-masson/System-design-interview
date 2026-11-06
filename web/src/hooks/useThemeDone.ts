import { type Dispatch, type SetStateAction, useState } from "react";
import { useI18n } from "../i18n";
import type { Theme } from "../types";

interface ThemeDone {
  pendingSlug: string | null;
  error: string | null;
  toggle: (theme: Theme) => Promise<void>;
}

/** Coche / décoche un thème : sauvegarde en base puis met la liste à jour. */
export function useThemeDone(
  save: (slug: string, fait: boolean) => Promise<void>,
  setThemes: Dispatch<SetStateAction<Theme[] | null>>,
): ThemeDone {
  const { t } = useI18n();
  const [pendingSlug, setPendingSlug] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const toggle = async (theme: Theme): Promise<void> => {
    setPendingSlug(theme.slug);
    setError(null);
    try {
      await save(theme.slug, !theme.fait);
      setThemes((current) =>
        (current ?? []).map((item) =>
          item.slug === theme.slug ? { ...item, fait: !theme.fait } : item,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : t("progress.saveFailed"));
    } finally {
      setPendingSlug(null);
    }
  };

  return { pendingSlug, error, toggle };
}
