import { CaptureUpdateAction, Excalidraw, restoreElements } from "@excalidraw/excalidraw";
import "@excalidraw/excalidraw/index.css";
import type { ExcalidrawElement } from "@excalidraw/excalidraw/element/types";
import type { ExcalidrawImperativeAPI, ExcalidrawInitialDataState } from "@excalidraw/excalidraw/types";
import { type Ref, useCallback, useEffect, useImperativeHandle, useRef, useState } from "react";
import { getSceneVersion, listSceneVersions, saveScene } from "../api";
import { useAppTheme } from "../hooks/useAppTheme";
import { useAutosave } from "../hooks/useAutosave";
import { buildLibraryItems } from "../sdLibrary";
import type { SceneElement, SceneVersion, StoredScene } from "../types";

const DEBOUNCE_MS = 2000;
const MAX_WAIT_MS = 30_000;
const KEEPALIVE_MAX_CHARS = 60_000;
const DEFAULT_BACKGROUND = "#ffffff";

export interface SdCanvasHandle {
  /** Enregistre immédiatement les modifications en attente et attend la fin de l'envoi. */
  flush: () => Promise<void>;
}

interface SdCanvasProps {
  sessionId: number;
  initialScene: StoredScene | null;
  readOnly: boolean;
  getElapsed: () => number;
  ref?: Ref<SdCanvasHandle>;
}

interface Snapshot {
  elements: SceneElement[];
  background: string;
  signature: string;
}

type SaveStatus =
  | { kind: "idle" }
  | { kind: "saving" }
  | { kind: "saved"; at: Date }
  | { kind: "error"; message: string };

const toElements = (elements: SceneElement[]): ExcalidrawElement[] =>
  elements as unknown as ExcalidrawElement[];

function backgroundOf(scene: StoredScene | null): string {
  const value = scene?.app_state.viewBackgroundColor;
  return typeof value === "string" ? value : DEFAULT_BACKGROUND;
}

function signatureOf(elements: readonly { id: string; version: number }[], background: string): string {
  return `${background}|${elements.map((e) => `${e.id}:${e.version}`).join(",")}`;
}

const formatTime = (date: Date): string =>
  date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });

export default function SdCanvas({ sessionId, initialScene, readOnly, getElapsed, ref }: SdCanvasProps) {
  const theme = useAppTheme();
  const apiRef = useRef<ExcalidrawImperativeAPI | null>(null);
  const [initialData] = useState<ExcalidrawInitialDataState>(() => ({
    elements: initialScene ? toElements(initialScene.elements) : [],
    appState: { viewBackgroundColor: backgroundOf(initialScene) },
    scrollToContent: true,
    libraryItems: buildLibraryItems(),
  }));
  const lastSignature = useRef(
    signatureOf(
      (initialScene?.elements ?? []) as unknown as { id: string; version: number }[],
      backgroundOf(initialScene),
    ),
  );
  const inFlight = useRef<Promise<void>>(Promise.resolve());
  const keepaliveNext = useRef(false);
  const unsaved = useRef<Snapshot | null>(null);
  const [status, setStatus] = useState<SaveStatus>({ kind: "idle" });
  const [versions, setVersions] = useState<SceneVersion[] | null>(null);
  const [versionsOpen, setVersionsOpen] = useState(false);

  const save = useCallback(
    (snapshot: Snapshot): void => {
      const keepalive = keepaliveNext.current;
      keepaliveNext.current = false;
      setStatus({ kind: "saving" });
      const body = { viewBackgroundColor: snapshot.background };
      const send = (): Promise<void> =>
        saveScene(
          sessionId,
          snapshot.elements,
          body,
          getElapsed(),
          keepalive && JSON.stringify(snapshot.elements).length < KEEPALIVE_MAX_CHARS,
        ).then(
          () => {
            unsaved.current = null;
            setStatus({ kind: "saved", at: new Date() });
            setVersions(null);
          },
          (err: unknown) => {
            unsaved.current = snapshot;
            setStatus({
              kind: "error",
              message: err instanceof Error ? err.message : "Échec de l'enregistrement.",
            });
          },
        );
      inFlight.current = inFlight.current.then(send);
    },
    [sessionId, getElapsed],
  );

  const autosave = useAutosave(save, DEBOUNCE_MS, MAX_WAIT_MS);

  useImperativeHandle(
    ref,
    () => ({
      flush: async () => {
        autosave.flush();
        await inFlight.current;
      },
    }),
    [autosave],
  );

  useEffect(() => {
    const onHide = (): void => {
      if (document.visibilityState === "hidden") {
        keepaliveNext.current = true;
        autosave.flush();
      }
    };
    document.addEventListener("visibilitychange", onHide);
    return () => {
      document.removeEventListener("visibilitychange", onHide);
      autosave.flush();
    };
  }, [autosave]);

  const handleChange = (elements: readonly ExcalidrawElement[], appState: { viewBackgroundColor: string }): void => {
    if (readOnly) return;
    const signature = signatureOf(elements, appState.viewBackgroundColor);
    if (signature === lastSignature.current) return;
    lastSignature.current = signature;
    autosave.schedule({
      elements: elements.filter((e) => !e.isDeleted) as unknown as SceneElement[],
      background: appState.viewBackgroundColor,
      signature,
    });
  };

  const retry = (): void => {
    if (unsaved.current) save(unsaved.current);
  };

  const toggleVersions = (): void => {
    const next = !versionsOpen;
    setVersionsOpen(next);
    if (next && versions === null) {
      listSceneVersions(sessionId)
        .then(setVersions)
        .catch((err: Error) => setStatus({ kind: "error", message: err.message }));
    }
  };

  const restore = (version: number): void => {
    getSceneVersion(sessionId, version)
      .then((scene) => {
        apiRef.current?.updateScene({
          elements: restoreElements(toElements(scene.elements), null),
          appState: { viewBackgroundColor: backgroundOf(scene) },
          captureUpdate: CaptureUpdateAction.IMMEDIATELY,
        });
        setVersionsOpen(false);
      })
      .catch((err: Error) => setStatus({ kind: "error", message: err.message }));
  };

  return (
    <section className="sd-canvas-wrap" aria-label="Schéma d'architecture">
      <div className="sd-canvas-bar">
        <p className="muted sd-save-status" role="status">
          {status.kind === "saving" && "Enregistrement…"}
          {status.kind === "saved" && `Enregistré à ${formatTime(status.at)}`}
          {status.kind === "idle" && (readOnly ? "Schéma en lecture seule" : "Sauvegarde automatique")}
          {status.kind === "error" && `Échec de l'enregistrement : ${status.message}`}
        </p>
        {status.kind === "error" && (
          <button type="button" className="btn" onClick={retry}>
            Réessayer
          </button>
        )}
        <button
          type="button"
          className="btn"
          aria-expanded={versionsOpen}
          disabled={readOnly}
          onClick={toggleVersions}
        >
          Versions
        </button>
      </div>
      {versionsOpen && (
        <div className="card sd-versions" role="region" aria-label="Versions du schéma">
          {versions === null && <p className="muted">Chargement…</p>}
          {versions?.length === 0 && <p className="muted">Aucune version enregistrée pour l&apos;instant.</p>}
          <ul>
            {versions?.map((v) => (
              <li key={v.version}>
                <button type="button" className="btn" onClick={() => restore(v.version)}>
                  Version {v.version} · {new Date(v.created_at).toLocaleString("fr-FR")}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="sd-canvas">
        <Excalidraw
          initialData={initialData}
          excalidrawAPI={(api) => {
            apiRef.current = api;
          }}
          onChange={(elements, appState) => handleChange(elements, appState)}
          theme={theme}
          langCode="fr-FR"
          viewModeEnabled={readOnly}
          UIOptions={{ tools: { image: false } }}
        />
      </div>
      <p className="muted sd-shortcuts">
        Clique sur le schéma pour utiliser les raccourcis Excalidraw : R rectangle, D losange, O ellipse,
        A flèche, T texte, Ctrl+D dupliquer, double-clic dans une forme pour écrire. Les cylindres sont dans
        le panneau Bibliothèque.
      </p>
    </section>
  );
}
