import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import type { GroupUsage, UsageSummary } from "../types";
import Consommation from "./Consommation";

vi.mock("../api");

const row = (group: string, calls: number, tokens: number, cost: number): GroupUsage => ({
  group,
  calls,
  tokens_in: tokens,
  tokens_out: 0,
  cost_estimate: cost,
});

const USAGE: UsageSummary = {
  total: row("total", 5, 3000, 0.0123),
  by_group: [
    row("cours", 2, 1000, 0.004),
    row("workflows", 1, 500, 0.002),
    row("manager", 2, 1500, 0.0063),
    row("system_design", 0, 0, 0),
  ],
  timeline: [
    { at: "2026-11-05T10:00:00+00:00", tokens: 400 },
    { at: "2026-11-05T11:00:00+00:00", tokens: 900 },
  ],
};

describe("Consommation", () => {
  beforeEach(() => vi.resetAllMocks());

  it("affiche les tokens et le prix au total, par exercice, et la courbe", async () => {
    vi.mocked(api.getUsage).mockResolvedValue(USAGE);
    render(<Consommation />);
    expect(await screen.findByText("Tokens au total")).toBeInTheDocument();
    expect(screen.getByText("Prix estimé au total")).toBeInTheDocument();
    const manager = screen.getByText("Entretien manager").closest(".usage-group");
    expect(manager).not.toBeNull();
    expect(within(manager as HTMLElement).getByText(/1\s?500/)).toBeInTheDocument();
    expect(screen.getByText("Mistral Workflows")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: "Courbe des tokens consommés par appel" })).toBeInTheDocument();
  });

  it("demande 2 appels minimum pour tracer la courbe", async () => {
    vi.mocked(api.getUsage).mockResolvedValue({ ...USAGE, timeline: [USAGE.timeline[0]] });
    render(<Consommation />);
    expect(await screen.findByText("Il faut au moins 2 appels pour tracer la courbe.")).toBeInTheDocument();
  });

  it("affiche l'état vide sans appel", async () => {
    vi.mocked(api.getUsage).mockResolvedValue({
      total: row("total", 0, 0, 0),
      by_group: [],
      timeline: [],
    });
    render(<Consommation />);
    expect(await screen.findByText("Aucun appel IA")).toBeInTheDocument();
  });

  it("affiche l'erreur de l'API", async () => {
    vi.mocked(api.getUsage).mockRejectedValue(new Error("API injoignable"));
    render(<Consommation />);
    expect(await screen.findByText("API injoignable")).toBeInTheDocument();
  });
});
