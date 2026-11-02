import { useEffect, useState } from "react";

export type AppTheme = "light" | "dark";

const DARK_QUERY = "(prefers-color-scheme: dark)";

function currentTheme(): AppTheme {
  const forced = document.documentElement.dataset.theme;
  if (forced === "light" || forced === "dark") return forced;
  return window.matchMedia(DARK_QUERY).matches ? "dark" : "light";
}

/** Thème actif de l'application (bascule manuelle ou préférence du système). */
export function useAppTheme(): AppTheme {
  const [theme, setTheme] = useState<AppTheme>(currentTheme);

  useEffect(() => {
    const update = (): void => setTheme(currentTheme());
    const observer = new MutationObserver(update);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    const media = window.matchMedia(DARK_QUERY);
    media.addEventListener("change", update);
    return () => {
      observer.disconnect();
      media.removeEventListener("change", update);
    };
  }, []);

  return theme;
}
