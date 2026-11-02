import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSession, requestFeedback, requestRelance, sendAnswer } from "../api";
import AnswerComposer from "../components/AnswerComposer";
import Conversation from "../components/Conversation";
import FeedbackView from "../components/FeedbackView";
import ScenarioCard from "../components/ScenarioCard";
import type { Session } from "../types";

type Busy = "answer" | "relance" | "feedback";

const BUSY_LABELS: Record<Busy, string> = {
  answer: "Enregistrement de ta réponse…",
  relance: "Le manager réfléchit à une relance…",
  feedback: "Le manager prépare ton retour…",
};

const errorMessage = (err: unknown): string =>
  err instanceof Error ? err.message : "Une erreur est survenue.";

export default function ManagerSession() {
  const sessionId = Number(useParams().id);
  const [session, setSession] = useState<Session | null>(null);
  const [busy, setBusy] = useState<Busy | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getSession(sessionId)
      .then(setSession)
      .catch((err: unknown) => setError(errorMessage(err)));
  }, [sessionId]);

  const run = useCallback(
    async (step: Busy, action: () => Promise<Session>): Promise<boolean> => {
      setBusy(step);
      setError(null);
      try {
        setSession(await action());
        return true;
      } catch (err) {
        setError(errorMessage(err));
        return false;
      } finally {
        setBusy(null);
      }
    },
    [],
  );

  const handleSubmit = async (text: string, durationS: number): Promise<boolean> => {
    const saved = await run("answer", () => sendAnswer(sessionId, text, durationS));
    if (!saved) return false;
    await run("relance", () => requestRelance(sessionId));
    return true;
  };

  if (!session) {
    return (
      <section>
        <h1>Entretien manager</h1>
        {error ? <div className="notice notice-error">{error}</div> : <p className="muted">Chargement…</p>}
      </section>
    );
  }

  const lastTurn = session.turns[session.turns.length - 1];
  const finished = session.feedback !== null;
  const waitingRelance =
    !finished && lastTurn?.kind === "answer" && session.answers_count < session.max_answers;
  const canAnswer = !finished && !waitingRelance && session.answers_count < session.max_answers;
  const canFinish = !finished && session.answers_count > 0;

  return (
    <section>
      <p>
        <Link to="/entretien-manager" className="muted">
          ← Entretien manager
        </Link>
      </p>
      <h1>Entretien manager</h1>
      <ScenarioCard question={session.question} />
      <Conversation turns={session.turns} />
      {busy && (
        <p className="muted" role="status">
          {BUSY_LABELS[busy]}
        </p>
      )}
      {error && <div className="notice notice-error">{error}</div>}
      {waitingRelance && !busy && (
        <div className="card">
          <p className="muted">La relance du manager n&apos;a pas pu être obtenue.</p>
          <button type="button" className="btn" onClick={() => void run("relance", () => requestRelance(sessionId))}>
            Réessayer la relance
          </button>
        </div>
      )}
      {canAnswer && (
        <>
          <p className="muted">
            Échange {session.answers_count + 1} sur {session.max_answers}
          </p>
          <AnswerComposer busy={busy !== null} onSubmit={handleSubmit} />
        </>
      )}
      {canFinish && (
        <div className="finish">
          <button
            type="button"
            className="btn btn-primary"
            disabled={busy !== null}
            onClick={() => void run("feedback", () => requestFeedback(sessionId))}
          >
            Terminer et obtenir le retour
          </button>
        </div>
      )}
      {session.feedback && (
        <>
          <FeedbackView feedback={session.feedback} />
          <div className="finish">
            <Link to="/entretien-manager" className="btn btn-primary">
              Nouvelle question
            </Link>
            <Link to="/historique" className="btn">
              Historique
            </Link>
          </div>
        </>
      )}
    </section>
  );
}
