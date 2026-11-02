import { act, createRef } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../api";
import { STORED_SCENE } from "../test/sdFixtures";
import { excalidraw } from "../test/mockExcalidraw";
import SdCanvas, { type SdCanvasHandle } from "./SdCanvas";

vi.mock("@excalidraw/excalidraw", async () => (await import("../test/mockExcalidraw")).excalidrawModule);
vi.mock("@excalidraw/excalidraw/index.css", () => ({}));
vi.mock("../api");

const DEBOUNCE_MS = 2000;
const MAX_WAIT_MS = 30_000;
const BACKGROUND = "#ffffff";

const element = (id: string, version: number, deleted = false) => ({
  id,
  type: "rectangle",
  version,
  isDeleted: deleted,
});

function change(elements: unknown[], background = BACKGROUND): void {
  act(() => excalidraw.props?.onChange?.(elements, { viewBackgroundColor: background }));
}

function renderCanvas(props: Partial<React.ComponentProps<typeof SdCanvas>> = {}) {
  return render(
    <SdCanvas
      sessionId={5}
      initialScene={STORED_SCENE}
      readOnly={false}
      getElapsed={() => 600}
      {...props}
    />,
  );
}

describe("SdCanvas", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.resetAllMocks();
    excalidraw.props = null;
    vi.mocked(api.saveScene).mockResolvedValue({ version: 3, created_at: "2026-11-02T10:31:00+00:00" });
  });

  afterEach(() => vi.useRealTimers());

  it("charge la dernière scène, en français, thème suivi, outil image désactivé", () => {
    renderCanvas();
    const props = excalidraw.props;
    expect(props?.initialData?.elements).toEqual(STORED_SCENE.elements);
    expect(props?.initialData?.appState).toEqual({ viewBackgroundColor: "#ffffff" });
    expect(props?.langCode).toBe("fr-FR");
    expect(props?.UIOptions?.tools?.image).toBe(false);
    expect(props?.viewModeEnabled).toBe(false);
    expect(props?.theme).toMatch(/light|dark/);
  });

  it("précharge la bibliothèque de formes dont le cylindre de base de données", () => {
    renderCanvas({ initialScene: null });
    const items = excalidraw.props?.initialData?.libraryItems as { id: string; name: string }[];
    expect(items.map((item) => item.id)).toEqual(["lib-database", "lib-queue", "lib-cloud", "lib-user"]);
    expect(items[0].name).toContain("cylindre");
  });

  it("démarre vide quand la session n'a pas encore de schéma", () => {
    renderCanvas({ initialScene: null });
    expect(excalidraw.props?.initialData?.elements).toEqual([]);
  });

  it("n'enregistre rien tant que la scène n'a pas changé", async () => {
    renderCanvas();
    change(STORED_SCENE.elements);
    await act(() => vi.advanceTimersByTimeAsync(MAX_WAIT_MS * 2));
    expect(api.saveScene).not.toHaveBeenCalled();
  });

  it("enregistre automatiquement après un délai sans modification, sans les éléments supprimés", async () => {
    renderCanvas();
    change([element("a", 4), element("z", 2, true)]);
    expect(api.saveScene).not.toHaveBeenCalled();
    await act(() => vi.advanceTimersByTimeAsync(DEBOUNCE_MS));
    expect(api.saveScene).toHaveBeenCalledTimes(1);
    expect(api.saveScene).toHaveBeenCalledWith(
      5,
      [element("a", 4)],
      { viewBackgroundColor: BACKGROUND },
      600,
      false,
    );
    expect(screen.getByText(/Enregistré à/)).toBeInTheDocument();
  });

  it("regroupe plusieurs modifications rapprochées en un seul enregistrement", async () => {
    renderCanvas();
    for (const version of [4, 5, 6]) {
      change([element("a", version)]);
      await act(() => vi.advanceTimersByTimeAsync(DEBOUNCE_MS / 2));
    }
    await act(() => vi.advanceTimersByTimeAsync(DEBOUNCE_MS));
    expect(api.saveScene).toHaveBeenCalledTimes(1);
    expect(vi.mocked(api.saveScene).mock.calls[0][1]).toEqual([element("a", 6)]);
  });

  it("enregistre au plus tard après le délai maximal même si l'on dessine sans arrêt", async () => {
    renderCanvas();
    for (let version = 4; version < 4 + 35; version += 1) {
      change([element("a", version)]);
      await act(() => vi.advanceTimersByTimeAsync(1000));
    }
    expect(vi.mocked(api.saveScene).mock.calls.length).toBeGreaterThanOrEqual(1);
  });

  it("signale un échec d'enregistrement et permet de réessayer", async () => {
    vi.mocked(api.saveScene).mockRejectedValueOnce(new Error("API injoignable"));
    renderCanvas();
    change([element("a", 4)]);
    await act(() => vi.advanceTimersByTimeAsync(DEBOUNCE_MS));
    expect(screen.getByText(/Échec de l'enregistrement : API injoignable/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Réessayer" }));
    await act(() => vi.advanceTimersByTimeAsync(0));
    expect(api.saveScene).toHaveBeenCalledTimes(2);
    expect(screen.getByText(/Enregistré à/)).toBeInTheDocument();
  });

  it("enregistre immédiatement sur demande (avant de terminer la session)", async () => {
    const ref = createRef<SdCanvasHandle>();
    renderCanvas({ ref });
    change([element("a", 9)]);
    await act(async () => {
      await ref.current?.flush();
    });
    expect(api.saveScene).toHaveBeenCalledTimes(1);
  });

  it("enregistre ce qui est en attente quand on quitte la page", async () => {
    const { unmount } = renderCanvas();
    change([element("a", 4)]);
    unmount();
    await vi.advanceTimersByTimeAsync(0);
    expect(api.saveScene).toHaveBeenCalledTimes(1);
  });

  it("enregistre en priorité quand l'onglet passe en arrière-plan (keepalive)", async () => {
    renderCanvas();
    change([element("a", 4)]);
    Object.defineProperty(document, "visibilityState", { value: "hidden", configurable: true });
    fireEvent(document, new Event("visibilitychange"));
    Object.defineProperty(document, "visibilityState", { value: "visible", configurable: true });
    await vi.advanceTimersByTimeAsync(0);
    expect(api.saveScene).toHaveBeenCalledTimes(1);
    expect(vi.mocked(api.saveScene).mock.calls[0][4]).toBe(true);
  });

  it("est en lecture seule et n'enregistre jamais une fois la session terminée", async () => {
    renderCanvas({ readOnly: true });
    expect(excalidraw.props?.viewModeEnabled).toBe(true);
    change([element("a", 4)]);
    await act(() => vi.advanceTimersByTimeAsync(MAX_WAIT_MS));
    expect(api.saveScene).not.toHaveBeenCalled();
    expect(screen.getByText("Schéma en lecture seule")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Versions" })).toBeDisabled();
  });

  it("liste les versions horodatées et restaure l'une d'elles dans le canvas", async () => {
    vi.useRealTimers();
    vi.mocked(api.listSceneVersions).mockResolvedValue([
      { version: 2, created_at: "2026-11-02T10:30:00+00:00" },
      { version: 1, created_at: "2026-11-02T10:10:00+00:00" },
    ]);
    vi.mocked(api.getSceneVersion).mockResolvedValue({
      version: 1,
      created_at: "2026-11-02T10:10:00+00:00",
      elements: [{ id: "old", type: "rectangle", version: 1 }],
      app_state: { viewBackgroundColor: "#eeeeee" },
    });
    renderCanvas();
    await userEvent.click(screen.getByRole("button", { name: "Versions" }));
    expect(await screen.findByRole("button", { name: /Version 1/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Version 2/ })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Version 1/ }));
    await waitFor(() => expect(excalidraw.updateScene).toHaveBeenCalledTimes(1));
    expect(excalidraw.updateScene).toHaveBeenCalledWith({
      elements: [{ id: "old", type: "rectangle", version: 1 }],
      appState: { viewBackgroundColor: "#eeeeee" },
      captureUpdate: "IMMEDIATELY",
    });
  });
});
