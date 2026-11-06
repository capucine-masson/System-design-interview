import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import { setLang } from "./i18n";

// jsdom n'implémente pas matchMedia (utilisé pour suivre le thème clair/sombre).
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string): MediaQueryList =>
    ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }) as unknown as MediaQueryList,
});

afterEach(() => {
  cleanup();
  setLang("fr");
  localStorage.clear();
});
