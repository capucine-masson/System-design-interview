import type { ReactNode } from "react";
import { type Lang, setLang, useI18n } from "../i18n";

const FLAG_W = 24;
const FLAG_H = 16;

/** Drapeaux dessinés en SVG : les emojis de drapeaux ne s'affichent pas sous Windows. */
const FLAGS: Record<Lang, ReactNode> = {
  fr: (
    <svg viewBox="0 0 3 2" width={FLAG_W} height={FLAG_H} aria-hidden="true">
      <rect width="1" height="2" fill="#0055a4" />
      <rect x="1" width="1" height="2" fill="#ffffff" />
      <rect x="2" width="1" height="2" fill="#ef4135" />
    </svg>
  ),
  en: (
    <svg viewBox="0 0 60 40" width={FLAG_W} height={FLAG_H} aria-hidden="true">
      <rect width="60" height="40" fill="#012169" />
      <path d="M0 0L60 40M60 0L0 40" stroke="#ffffff" strokeWidth="8" />
      <path d="M0 0L60 40M60 0L0 40" stroke="#c8102e" strokeWidth="3" />
      <path d="M30 0V40M0 20H60" stroke="#ffffff" strokeWidth="12" />
      <path d="M30 0V40M0 20H60" stroke="#c8102e" strokeWidth="7" />
    </svg>
  ),
};

const LANGS: { value: Lang; label: string }[] = [
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
];

/** Bascule la langue de toute l'application (interface et réponses de l'IA). */
export default function LanguageToggle() {
  const { lang, t } = useI18n();
  return (
    <div className="lang-toggle" role="group" aria-label={t("app.language")}>
      {LANGS.map((item) => (
        <button
          key={item.value}
          type="button"
          className="lang-btn"
          lang={item.value}
          aria-pressed={lang === item.value}
          aria-label={item.label}
          title={item.label}
          onClick={() => setLang(item.value)}
        >
          {FLAGS[item.value]}
        </button>
      ))}
    </div>
  );
}
