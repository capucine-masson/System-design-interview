import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { getLang } from "../i18n";
import LanguageToggle from "./LanguageToggle";
import ThemeToggle from "./ThemeToggle";

describe("bouton de langue", () => {
  it("bascule en anglais : le bouton drapeau est coché et les textes changent", async () => {
    render(
      <>
        <LanguageToggle />
        <ThemeToggle />
      </>,
    );
    expect(screen.getByRole("button", { name: "Français" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("Mode sombre")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "English" }));

    expect(getLang()).toBe("en");
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Français" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("Dark mode")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Change theme" })).toBeInTheDocument();
  });

  it("envoie la langue choisie à l'API dans l'en-tête X-Lang", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response("[]", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<LanguageToggle />);
    await userEvent.click(screen.getByRole("button", { name: "English" }));

    await api.listCaseTypes();

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(new Headers(init.headers).get("X-Lang")).toBe("en");
    vi.unstubAllGlobals();
  });
});
