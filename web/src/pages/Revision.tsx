import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { drawCards, getThemes, reviewCard } from "../api";
import CourseReviewView from "../components/CourseReviewView";
import EmptyState from "../components/EmptyState";
import FlipCard from "../components/FlipCard";
import ProgressButtons from "../components/ProgressButtons";
import RevisionSetup from "../components/RevisionSetup";
import VoiceAnswer from "../components/VoiceAnswer";
import { useCardProgress } from "../hooks/useCardProgress";
import { translate, useI18n } from "../i18n";
import type { Card, CourseReview, RevisionCount, Statut, Theme } from "../types";

type Phase = "setup" | "question" | "correction" | "done";

const DEFAULT_COUNT: RevisionCount = 10;

function errorText(err: unknown, fallback: string): string {
  return err instanceof Error ? err.message : fallback;
}

/** Nombre de cartes tirables selon le thème (ou tous) et le filtre « à revoir ». */
function availableCards(themes: Theme[], slug: string | undefined, onlyToReview: boolean): number {
  return themes
    .filter((theme) => slug === undefined || theme.slug === slug)
    .reduce((sum, theme) => sum + (onlyToReview ? theme.a_revoir : theme.total), 0);
}

export default function Revision() {
  const { lang, t } = useI18n();
  const [params] = useSearchParams();
  const theme = params.get("theme") ?? undefined;
  const [themes, setThemes] = useState<Theme[]>([]);
  const [count, setCount] = useState<RevisionCount>(DEFAULT_COUNT);
  const [onlyToReview, setOnlyToReview] = useState(false);
  const [phase, setPhase] = useState<Phase>("setup");
  const [cards, setCards] = useState<Card[]>([]);
  const [index, setIndex] = useState(0);
  const [review, setReview] = useState<CourseReview | null>(null);
  const [marked, setMarked] = useState<Record<number, Statut | null>>({});
  const [loading, setLoading] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getThemes()
      .then(setThemes)
      .catch((err: unknown) => setError(errorText(err, translate("revision.drawFailed"))));
  }, [lang]);

  const progress = useCardProgress((saved, statut) => {
    setCards((current) => current.map((card) => (card.id === saved.id ? { ...card, statut } : card)));
    setMarked((current) => ({ ...current, [saved.id]: statut }));
  });

  const card = cards[index];
  const available = availableCards(themes, theme, onlyToReview);

  const start = async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const drawn = await drawCards({
        theme,
        statut: onlyToReview ? "a_revoir" : undefined,
        limit: count === "max" ? undefined : count,
      });
      setCards(drawn);
      setIndex(0);
      setMarked({});
      setReview(null);
      setPhase("question");
    } catch (err) {
      setError(errorText(err, translate("revision.drawFailed")));
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async (text: string): Promise<boolean> => {
    setReviewing(true);
    setError(null);
    try {
      setReview(await reviewCard(card.id, text));
      setPhase("correction");
      return true;
    } catch (err) {
      setError(errorText(err, translate("revision.reviewFailed")));
      return false;
    } finally {
      setReviewing(false);
    }
  };

  const next = (): void => {
    setReview(null);
    if (index + 1 >= cards.length) {
      setPhase("done");
      return;
    }
    setIndex(index + 1);
    setPhase("question");
  };

  const restart = (): void => {
    setPhase("setup");
    setError(null);
  };

  const masteredCount = Object.values(marked).filter((s) => s === "maitrisee").length;
  const toReviewCount = Object.values(marked).filter((s) => s === "a_revoir").length;

  return (
    <section className="revision-page">
      <p>
        <Link to={theme ? `/cours/${theme}` : "/cours"} className="muted">
          {t("revision.back")}
        </Link>
      </p>
      <div className="page-head">
        <h1>{t("revision.title")}</h1>
        {(phase === "question" || phase === "correction") && (
          <span className="muted">
            {t("revision.progress", { current: index + 1, total: cards.length })}
          </span>
        )}
      </div>

      {phase === "setup" && (
        <>
          <RevisionSetup
            available={available}
            count={count}
            onlyToReview={onlyToReview}
            loading={loading}
            onCount={setCount}
            onToggleToReview={() => setOnlyToReview((value) => !value)}
            onStart={() => void start()}
          />
          {error && (
            <EmptyState
              title={onlyToReview ? t("courses.nothingToReview") : t("courses.noCards")}
              hint={error}
            />
          )}
        </>
      )}

      {phase === "question" && card && (
        <div className="revision-stage revision-question">
          <p className="muted revision-label">{t("revision.prompt")}</p>
          <h2 className="revision-notion">{card.titre}</h2>
          <VoiceAnswer busy={reviewing} onSubmit={submitAnswer} />
          {error && <div className="card error">{error}</div>}
        </div>
      )}

      {phase === "correction" && card && review && (
        <div className="revision-stage">
          <div className="review-head">
            <h2 className="revision-notion">{card.titre}</h2>
            <div className="review-actions">
              <ProgressButtons
                statut={card.statut}
                disabled={progress.pendingId === card.id}
                onChange={(statut) => void progress.update(card, statut)}
              />
              <FlipCard
                key={card.id}
                card={card}
                variant="link"
                pending={progress.pendingId === card.id}
                onProgress={progress.update}
              />
              <button type="button" className="btn btn-primary" onClick={next}>
                {index + 1 >= cards.length ? t("revision.finish") : t("revision.next")}
              </button>
            </div>
          </div>
          {progress.error && <div className="card error">{progress.error}</div>}
          <CourseReviewView review={review} />
        </div>
      )}

      {phase === "done" && (
        <div className="card revision-setup">
          <h2>{t("revision.doneTitle")}</h2>
          <p>
            {t("revision.doneSummary", {
              n: cards.length,
              mastered: masteredCount,
              toReview: toReviewCount,
            })}
          </p>
          <button type="button" className="btn btn-primary" onClick={restart}>
            {t("revision.restart")}
          </button>
        </div>
      )}
    </section>
  );
}
