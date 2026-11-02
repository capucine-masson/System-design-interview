import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { QUESTION, SESSION } from "../test/managerFixtures";
import EntretienManager from "./EntretienManager";

vi.mock("../api");

const renderPage = () =>
  render(
    <MemoryRouter initialEntries={["/entretien-manager"]}>
      <Routes>
        <Route path="/entretien-manager" element={<EntretienManager />} />
        <Route path="/entretien-manager/sessions/:id" element={<p>Page de session</p>} />
      </Routes>
    </MemoryRouter>,
  );

describe("EntretienManager", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.listQuestions).mockResolvedValue([QUESTION, QUESTION]);
  });

  it("n'appelle l'IA qu'au clic, avec la catégorie et la difficulté choisies", async () => {
    vi.mocked(api.generateQuestion).mockResolvedValue(QUESTION);
    vi.mocked(api.createSession).mockResolvedValue(SESSION);
    renderPage();
    expect(await screen.findByText("Banque : 2 questions pour ce filtre.")).toBeInTheDocument();
    expect(api.generateQuestion).not.toHaveBeenCalled();

    await userEvent.selectOptions(screen.getByLabelText("Catégorie"), "technique");
    await userEvent.selectOptions(screen.getByLabelText("Difficulté"), "difficile");
    await userEvent.click(screen.getByRole("button", { name: "Générer une question" }));

    expect(api.generateQuestion).toHaveBeenCalledWith("technique", "difficile");
    expect(api.createSession).toHaveBeenCalledWith(QUESTION.id);
    expect(await screen.findByText("Page de session")).toBeInTheDocument();
  });

  it("tire de la banque sans appeler la génération", async () => {
    vi.mocked(api.drawQuestion).mockResolvedValue(QUESTION);
    vi.mocked(api.createSession).mockResolvedValue(SESSION);
    renderPage();
    await screen.findByText(/Banque : 2/);
    await userEvent.click(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" }));
    expect(api.drawQuestion).toHaveBeenCalledWith({ categorie: "mixte", difficulte: "moyenne" });
    expect(api.generateQuestion).not.toHaveBeenCalled();
    expect(await screen.findByText("Page de session")).toBeInTheDocument();
  });

  it("désactive le tirage quand la banque est vide", async () => {
    vi.mocked(api.listQuestions).mockResolvedValue([]);
    renderPage();
    await screen.findByText("Banque : 0 question pour ce filtre.");
    expect(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" })).toBeDisabled();
  });

  it("désactive les boutons pendant la génération", async () => {
    vi.mocked(api.generateQuestion).mockReturnValue(new Promise(() => undefined));
    renderPage();
    await screen.findByText(/Banque : 2/);
    await userEvent.click(screen.getByRole("button", { name: "Générer une question" }));
    expect(await screen.findByRole("button", { name: "Génération en cours…" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Tirer de la banque (sans IA)" })).toBeDisabled();
  });

  it("affiche un message lisible si la génération échoue et réactive les boutons", async () => {
    vi.mocked(api.generateQuestion).mockRejectedValue(new Error("Quota Mistral dépassé"));
    renderPage();
    await screen.findByText(/Banque : 2/);
    await userEvent.click(screen.getByRole("button", { name: "Générer une question" }));
    expect(await screen.findByText("Quota Mistral dépassé")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Générer une question" })).toBeEnabled());
    expect(api.createSession).not.toHaveBeenCalled();
  });
});
