import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  finishSdSession,
  getCorrection,
  getScene,
  getSdSession,
  postSdMessage,
  putElapsed,
  requestCorrection,
  requestSdReply,
} from "../api";
import SdCanvas, { type SdCanvasHandle } from "../components/SdCanvas";
import SdChat from "../components/SdChat";
import SdCorrectionView from "../components/SdCorrectionView";
import SdFinish from "../components/SdFinish";
import SdTimer from "../components/SdTimer";
import { useElapsed } from "../hooks/useElapsed";
import type { CorrectionBundle, SdSession, StoredScene } from "../types";

const ELAPSED_SYNC_MS = 30_000;

const errorMessage = (err: unknown): string =>
  err instanceof Error ? err.message : "Une erreur est survenue.";

interface Loaded {
  session: SdSession;
  scene: StoredScene | null;
}

export default function SystemDesignSession() {
  const sessionId = Number(useParams().id);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getSdSession(sessionId), getScene(sessionId)])
      .then(([session, scene]) => setLoaded({ session, scene }))
      .catch((err: unknown) => setError(errorMessage(err)));
  }, [sessionId]);

  if (!loaded) {
    return (
      <section>
        <h1>System Design</h1>
        {error ? <div className="notice notice-error">{error}</div> : <p className="muted">Chargement…</p>}
      </section>
    );
  }
  return <Workspace initial={loaded} sessionId={sessionId} />;
}

function Workspace({ initial, sessionId }: { initial: Loaded; sessionId: number }) {
  const [session, setSession] = useState(initial.session);
  const [busy, setBusy] = useState<"message" | "reply" | "finish" | "correction" | null>(null);
  const [bundle, setBundle] = useState<CorrectionBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<SdCanvasHandle>(null);
  const finished = session.statut === "terminee";
  const { elapsed, getElapsed } = useElapsed(session.elapsed_s, !finished);

  useEffect(() => {
    if (finished) return;
    const sync = (): void => {
      putElapsed(sessionId, getElapsed()).catch((err: unknown) =>
        console.warn("Synchronisation du temps impossible", err),
      );
    };
    const id = window.setInterval(sync, ELAPSED_SYNC_MS);
    return () => {
      window.clearInterval(id);
      sync();
    };
  }, [sessionId, finished, getElapsed]);

  useEffect(() => {
    if (!finished) return;
    getCorrection(sessionId)
      .then((found) => found && setBundle(found))
      .catch((err: unknown) => setError(errorMessage(err)));
  }, [finished, sessionId]);

  const askCorrection = useCallback(async (): Promise<void> => {
    setBusy("correction");
    setError(null);
    try {
      setBundle(await requestCorrection(sessionId));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }, [sessionId]);

  const askReply = useCallback(async (): Promise<void> => {
    setBusy("reply");
    setError(null);
    try {
      setSession(await requestSdReply(sessionId));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(null);
    }
  }, [sessionId]);

  const send = async (text: string): Promise<boolean> => {
    setBusy("message");
    setError(null);
    try {
      setSession(await postSdMessage(sessionId, text, getElapsed()));
    } catch (err) {
      setError(errorMessage(err));
      setBusy(null);
      return false;
    }
    await askReply();
    return true;
  };

  const finish = async (): Promise<void> => {
    setBusy("finish");
    setError(null);
    try {
      await canvasRef.current?.flush();
      await putElapsed(sessionId, getElapsed());
      setSession(await finishSdSession(sessionId));
    } catch (err) {
      setError(errorMessage(err));
      setBusy(null);
      return;
    }
    await askCorrection();
  };

  return (
    <section>
      <p>
        <Link to="/system-design" className="muted">
          ← System Design
        </Link>
      </p>
      <div className="page-head">
        <h1>{session.case.titre}</h1>
        <SdFinish finished={finished} busy={busy !== null} onFinish={finish} />
      </div>
      <SdTimer elapsed={elapsed} />
      <div className="sd-layout">
        <SdChat
          session={session}
          busy={busy === "message" || busy === "reply"}
          error={finished ? null : error}
          onSend={send}
          onRetryReply={() => void askReply()}
        />
        <SdCanvas
          ref={canvasRef}
          sessionId={sessionId}
          initialScene={initial.scene}
          readOnly={finished}
          getElapsed={getElapsed}
        />
      </div>
      {busy === "correction" && (
        <p className="muted" role="status">
          Le manager prépare la correction… (jusqu&apos;à une minute la première fois)
        </p>
      )}
      {finished && !bundle && busy !== "correction" && (
        <div className="card">
          <p>La correction détaillée et la solution de référence sont prêtes à être générées.</p>
          {error && <div className="notice notice-error">{error}</div>}
          <button type="button" className="btn btn-primary" onClick={() => void askCorrection()}>
            Obtenir la correction détaillée
          </button>
        </div>
      )}
      {bundle && <SdCorrectionView bundle={bundle} />}
    </section>
  );
}
