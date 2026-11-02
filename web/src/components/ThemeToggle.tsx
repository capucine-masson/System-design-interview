import { useState } from "react";

type Theme = "light" | "dark";
const STORAGE_KEY = "theme";

function systemTheme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function initialTheme(): Theme {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === "light" || saved === "dark" ? saved : systemTheme();
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => {
    const initial = initialTheme();
    document.documentElement.dataset.theme = initial;
    return initial;
  });

  const toggle = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem(STORAGE_KEY, next);
    setTheme(next);
  };

  return (
    <button className="btn" onClick={toggle} aria-label="Changer de thème">
      {theme === "dark" ? "Mode clair" : "Mode sombre"}
    </button>
  );
}
