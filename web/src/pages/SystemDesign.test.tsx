import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { CASE_TYPES, SD_SESSION, SD_SUMMARY } from "../test/sdFixtures";
import SystemDesign from "./SystemDesign";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={["/system-design"]}>
      <Routes>
        <Route path="/system-design" element={<SystemDesign />} />
        <Route path="/system-design/sessions/:id" element={<p>Page de session</p>} />
      </Routes>
    </MemoryRouter>,
  );

describe("SystemDesign (choix du cas)", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.listCaseTypes).mockResolvedValue(CASE_TYPES);
    vi.mocked(api.listSdSessions).mockResolvedValue([]);
    vi.mocked(api.createSdSession).mockResolvedValue(SD_SESSION);
  });

  afterEach(() => vi.restoreAllMocks());

  it("affiche les cas du catalogue venant de l'API, plus « Au hasard », sans appel IA", async () => {
    renderPage();
    expect(await screen.findByLabelText(/RAG sur une grande base documentaire/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Agent ou assistant avec outils/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Au hasard/)).toBeChecked();
    expect(api.generateCase).not.toHaveBeenCalled();
  });

  it("génère un brief pour le cas choisi puis ouvre la session", async () => {
    vi.mocked(api.generateCase).mockResolvedValue(SD_SESSION.case);
    renderPage();
    await userEvent.click(await screen.findByLabelText(/Agent ou assistant avec outils/));
    await userEvent.click(screen.getByRole("button", { name: "Générer un brief" }));
    expect(api.generateCase).toHaveBeenCalledWith("agent");
    expect(api.createSdSession).toHaveBeenCalledWith(SD_SESSION.case.id);
    expect(await screen.findByText("Page de session")).toBeInTheDocument();
  });

  it("tire un type au hasard quand « Au hasard » est choisi", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0.99);
    vi.mocked(api.generateCase).mockResolvedValue(SD_SESSION.case);
    renderPage();
    await screen.findByLabelText(/Au hasard/);
    await userEvent.click(screen.getByRole("button", { name: "Générer un brief" }));
    expect(api.generateCase).toHaveBeenCalledWith("google-docs");
  });

  it("range les cas par famille : ML / LLM puis cas classiques", async () => {
    renderPage();
    await screen.findByLabelText(/Au hasard/);
    const ml = screen.getByRole("group", { name: "Systèmes ML / LLM" });
    const classic = screen.getByRole("group", { name: "Cas classiques d'entretien" });
    expect(within(ml).getByLabelText(/RAG sur une grande base/)).toBeInTheDocument();
    expect(within(ml).queryByLabelText(/Google Docs/)).not.toBeInTheDocument();
    expect(within(classic).getByLabelText(/Google Docs/)).toBeInTheDocument();
  });

  it("génère un brief pour un cas classique choisi", async () => {
    vi.mocked(api.generateCase).mockResolvedValue(SD_SESSION.case);
    renderPage();
    await userEvent.click(await screen.findByLabelText(/Google Docs/));
    await userEvent.click(screen.getByRole("button", { name: "Générer un brief" }));
    expect(api.generateCase).toHaveBeenCalledWith("google-docs");
  });

  it("tire de la banque sans appeler la génération", async () => {
    vi.mocked(api.drawCase).mockResolvedValue(SD_SESSION.case);
    renderPage();
    await userEvent.click(await screen.findByLabelText(/RAG sur une grande base documentaire/));
    await userEvent.click(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" }));
    expect(api.drawCase).toHaveBeenCalledWith("rag");
    expect(api.generateCase).not.toHaveBeenCalled();
    expect(await screen.findByText("Page de session")).toBeInTheDocument();
  });

  it("tire dans toute la banque avec « Au hasard »", async () => {
    vi.mocked(api.drawCase).mockResolvedValue(SD_SESSION.case);
    renderPage();
    await screen.findByLabelText(/Au hasard/);
    await userEvent.click(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" }));
    expect(api.drawCase).toHaveBeenCalledWith(undefined);
  });

  it("désactive les boutons pendant la génération", async () => {
    vi.mocked(api.generateCase).mockReturnValue(new Promise(() => undefined));
    renderPage();
    await screen.findByLabelText(/Au hasard/);
    await userEvent.click(screen.getByRole("button", { name: "Générer un brief" }));
    expect(await screen.findByRole("button", { name: "Génération du brief…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" })).toBeDisabled();
  });

  it("affiche un message lisible si la génération échoue", async () => {
    vi.mocked(api.generateCase).mockRejectedValue(new Error("Quota Mistral dépassé"));
    renderPage();
    await screen.findByLabelText(/Au hasard/);
    await userEvent.click(screen.getByRole("button", { name: "Générer un brief" }));
    expect(await screen.findByText("Quota Mistral dépassé")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Générer un brief" })).toBeEnabled());
    expect(api.createSdSession).not.toHaveBeenCalled();
  });

  it("affiche l'erreur si le catalogue est inaccessible", async () => {
    vi.mocked(api.listCaseTypes).mockRejectedValue(new Error("API injoignable"));
    renderPage();
    expect(await screen.findByText("API injoignable")).toBeInTheDocument();
  });

  it("propose de reprendre les sessions existantes", async () => {
    vi.mocked(api.listSdSessions).mockResolvedValue([SD_SUMMARY]);
    renderPage();
    const link = await screen.findByRole("link", { name: "Assistant documentaire interne" });
    expect(link).toHaveAttribute("href", "/system-design/sessions/5");
    expect(screen.getByText(/en cours/)).toBeInTheDocument();
  });
});
