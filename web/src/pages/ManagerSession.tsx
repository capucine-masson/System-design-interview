import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSession, requestFeedback, requestRelance, sendAnswer } from "../api";
import AnswerComposer from "../components/AnswerComposer";
import Conversation from "../components/Conversation";
import FeedbackView from "../components/FeedbackView";
import ScenarioCard from "../components/ScenarioCard";
import { translate, type TKey, useI18n } from "../i18n";
import type { Session } from "../types";

type Busy = "answer" | "relance" | "feedback";

const BUSY_LABELS: Record<Busy, TKey> = {
  answer: "manager.busy.answer",
  relance: "manager.busy.relance",
  feedback: "manager.busy.feedback",
};

const errorMessage = (err: unknown): string =>
  err instanceof Error ? err.message : translate("common.unknownError");

export default function ManagerSession() {
  const { t } = useI18n();
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
        <h1>{t("manager.title")}</h1>
        {error ? (
          <div className="notice notice-error">{error}</div>
        ) : (
          <p className="muted">{t("common.loading")}</p>
        )}
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
          {t("manager.back")}
        </Link>
      </p>
      <h1>{t("manager.title")}</h1>
      <ScenarioCard question={session.question} />
      <Conversation turns={session.turns} />
      {busy && (
        <p className="muted" role="status">
          {t(BUSY_LABELS[busy])}
        </p>
      )}
      {error && <div className="notice notice-error">{error}</div>}
      {waitingRelance && !busy && (
        <div className="card">
          <p className="muted">{t("manager.followupMissing")}</p>
          <button type="button" className="btn" onClick={() => void run("relance", () => requestRelance(sessionId))}>
            {t("manager.retryFollowup")}
          </button>
        </div>
      )}
      {canAnswer && (
        <>
          <p className="muted">
            {t("manager.exchange", { n: session.answers_count + 1, max: session.max_answers })}
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
            {t("manager.finish")}
          </button>
        </div>
      )}
      {session.feedback && (
        <>
          <FeedbackView feedback={session.feedback} />
          <div className="finish">
            <Link to="/entretien-manager" className="btn btn-primary">
              {t("manager.newQuestion")}
            </Link>
            <Link to="/historique" className="btn">
              {t("history.title")}
            </Link>
          </div>
        </>
      )}
    </section>
  );
}
