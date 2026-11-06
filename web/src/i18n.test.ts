import { describe, expect, it } from "vitest";
import { getLang, setLang, translate } from "./i18n";
import { en } from "./locales/en";
import { fr } from "./locales/fr";

describe("traduction", () => {
  it("a les mêmes clés en français et en anglais, sans texte vide", () => {
    expect(Object.keys(en).sort()).toEqual(Object.keys(fr).sort());
    for (const [key, text] of Object.entries(en)) expect(text, key).not.toBe("");
  });

  it("garde les mêmes paramètres {nom} dans les deux langues", () => {
    const params = (text: string): string[] => (text.match(/\{\w+\}/g) ?? []).sort();
    for (const [key, text] of Object.entries(fr)) {
      expect(params(en[key as keyof typeof en]), key).toEqual(params(text));
    }
  });

  it("remplace les paramètres", () => {
    expect(translate("manager.exchange", { n: 2, max: 3 }, "fr")).toBe("Échange 2 sur 3");
    expect(translate("manager.exchange", { n: 2, max: 3 }, "en")).toBe("Exchange 2 of 3");
  });

  it("change la langue, la mémorise et met à jour <html lang>", () => {
    expect(getLang()).toBe("fr");
    setLang("en");
    expect(getLang()).toBe("en");
    expect(localStorage.getItem("lang")).toBe("en");
    expect(document.documentElement.lang).toBe("en");
    expect(translate("common.loading")).toBe("Loading…");
  });
});
