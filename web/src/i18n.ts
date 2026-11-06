import { useCallback, useMemo, useSyncExternalStore } from "react";
import { en } from "./locales/en";
import { fr, type TKey } from "./locales/fr";

export type Lang = "fr" | "en";
export type { TKey };
export type Params = Record<string, string | number>;
export type Translate = (key: TKey, params?: Params) => string;

const STORAGE_KEY = "lang";
const DEFAULT_LANG: Lang = "fr";

const DICTIONARIES: Record<Lang, Record<TKey, string>> = { fr, en };
/** Locale de formatage des dates et des nombres. */
export const LOCALES: Record<Lang, string> = { fr: "fr-FR", en: "en-GB" };
/** Locale de la dictée vocale du navigateur. */
export const SPEECH_LOCALES: Record<Lang, string> = { fr: "fr-FR", en: "en-US" };
/** Code de langue d'Excalidraw. */
export const EXCALIDRAW_LOCALES: Record<Lang, string> = { fr: "fr-FR", en: "en" };

function readStoredLang(): Lang {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === "fr" || saved === "en" ? saved : DEFAULT_LANG;
  } catch {
    return DEFAULT_LANG; // stockage indisponible (navigation privée) : français
  }
}

let current: Lang = readStoredLang();
document.documentElement.lang = current;
const listeners = new Set<() => void>();

export const getLang = (): Lang => current;

/** Change la langue de toute l'application et la mémorise dans le navigateur. */
export function setLang(lang: Lang): void {
  if (lang === current) return;
  current = lang;
  document.documentElement.lang = lang;
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // pas de mémorisation possible : la langue vaut pour cette visite seulement
  }
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Traduit une clé dans la langue donnée (par défaut la langue courante) ; `{nom}` est remplacé. */
export function translate(key: TKey, params?: Params, lang: Lang = current): string {
  const text = DICTIONARIES[lang][key];
  if (!params) return text;
  return text.replace(/\{(\w+)\}/g, (match, name: string) =>
    name in params ? String(params[name]) : match,
  );
}

interface I18n {
  lang: Lang;
  t: Translate;
  locale: string;
}

/** Langue courante, fonction de traduction et locale ; le composant se redessine au changement. */
export function useI18n(): I18n {
  const lang = useSyncExternalStore(subscribe, getLang);
  const t = useCallback<Translate>((key, params) => translate(key, params, lang), [lang]);
  return useMemo(() => ({ lang, t, locale: LOCALES[lang] }), [lang, t]);
}
