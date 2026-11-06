import type {
  Card,
  CaseType,
  CorrectionBundle,
  CourseReview,
  Categorie,
  Difficulte,
  Question,
  SceneElement,
  SceneVersion,
  SdCase,
  SdSession,
  SdSessionSummary,
  Session,
  StoredScene,
  SessionSummary,
  Statut,
  Theme,
  UsageSummary,
} from "./types";
import { getLang, translate } from "./i18n";

const API_URL = import.meta.env.VITE_API_URL;
const HTTP_NO_CONTENT = 204;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

const LANG_HEADER = "X-Lang";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set(LANG_HEADER, getLang());
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new Error(translate("common.apiDown"));
  }
  if (!response.ok) {
    const body: { detail?: string } = await response.json().catch(() => ({}));
    throw new ApiError(
      typeof body.detail === "string"
        ? body.detail
        : translate("common.errorStatus", { status: response.status }),
      response.status,
    );
  }
  if (response.status === HTTP_NO_CONTENT) return undefined as T;
  return (await response.json()) as T;
}

function query(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) search.set(key, String(value));
  }
  const text = search.toString();
  return text ? `?${text}` : "";
}

const post = <T>(path: string, body?: unknown): Promise<T> =>
  request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

export const getUsage =(): Promise<UsageSummary> => request<UsageSummary>("/api/usage");

export const getThemes = (): Promise<Theme[]> => request<Theme[]>("/api/themes");

export const setThemeDone = (slug: string, fait: boolean): Promise<void> =>
  request<void>(`/api/themes/${encodeURIComponent(slug)}/done`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fait }),
  });

export const getCards = (slug: string, statut?: Statut): Promise<Card[]> =>
  request<Card[]>(`/api/themes/${encodeURIComponent(slug)}/cards${query({ statut })}`);

/** Série de cartes distinctes tirées au hasard ; sans `limit`, toutes les cartes (« max »). */
export const drawCards = (options: {
  theme?: string;
  statut?: Statut;
  limit?: number;
}): Promise<Card[]> => request<Card[]>(`/api/cards/draw${query(options)}`);

/** Correction IA de l'explication orale d'une carte (un appel IA, sur clic uniquement). */
export const reviewCard = (cardId: number, transcription: string): Promise<CourseReview> =>
  post<CourseReview>(`/api/cards/${cardId}/review`, { transcription });

export const setProgress = (cardId: number, statut: Statut | null): Promise<void> =>
  request<void>(`/api/cards/${cardId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ statut }),
  });

// --- Mistral Workflows (mêmes formes que les Cours, tables et routes séparées) ---

const WORKFLOWS = "/api/workflows";

export const getWorkflowThemes = (): Promise<Theme[]> =>
  request<Theme[]>(`${WORKFLOWS}/themes`);

export const setWorkflowThemeDone = (slug: string, fait: boolean): Promise<void> =>
  request<void>(`${WORKFLOWS}/themes/${encodeURIComponent(slug)}/done`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fait }),
  });

export const getWorkflowCards =(slug: string, statut?: Statut): Promise<Card[]> =>
  request<Card[]>(`${WORKFLOWS}/themes/${encodeURIComponent(slug)}/cards${query({ statut })}`);

export const drawWorkflowCards = (options: {
  theme?: string;
  statut?: Statut;
  limit?: number;
}): Promise<Card[]> => request<Card[]>(`${WORKFLOWS}/cards/draw${query(options)}`);

/** Correction IA de l'explication orale d'une carte Workflows (un appel IA, sur clic uniquement). */
export const reviewWorkflowCard = (cardId: number, transcription: string): Promise<CourseReview> =>
  post<CourseReview>(`${WORKFLOWS}/cards/${cardId}/review`, { transcription });

export const setWorkflowProgress = (cardId: number, statut: Statut | null): Promise<void> =>
  request<void>(`${WORKFLOWS}/cards/${cardId}/progress`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ statut }),
  });

// --- Entretien manager (les appels IA ne partent que sur ces actions explicites) ---

interface QuestionFilter {
  categorie?: Categorie;
  difficulte?: Difficulte;
}

export const listQuestions = (filter: QuestionFilter): Promise<Question[]> =>
  request<Question[]>(`/api/manager/questions${query({ ...filter })}`);

export const drawQuestion = (filter: QuestionFilter): Promise<Question> =>
  request<Question>(`/api/manager/questions/draw${query({ ...filter })}`);

export const generateQuestion = (categorie: Categorie, difficulte: Difficulte): Promise<Question> =>
  post<Question>("/api/manager/questions/generate", { categorie, difficulte });

export const createSession = (questionId: number): Promise<Session> =>
  post<Session>("/api/manager/sessions", { question_id: questionId });

export const getSession = (id: number): Promise<Session> =>
  request<Session>(`/api/manager/sessions/${id}`);

export const listSessions = (): Promise<SessionSummary[]> =>
  request<SessionSummary[]>("/api/manager/sessions");

export const sendAnswer = (id: number, transcription: string, dureeS: number): Promise<Session> =>
  post<Session>(`/api/manager/sessions/${id}/answers`, { transcription, duree_s: dureeS });

export const requestRelance = (id: number): Promise<Session> =>
  post<Session>(`/api/manager/sessions/${id}/relance`);

export const requestFeedback = (id: number): Promise<Session> =>
  post<Session>(`/api/manager/sessions/${id}/feedback`);

// --- System Design (les appels IA ne partent que sur generateCase et requestSdReply) ---

const HTTP_NOT_FOUND = 404;
const sd = (path: string): string => `/api/sd${path}`;

export const listCaseTypes = (): Promise<CaseType[]> => request<CaseType[]>(sd("/case-types"));

export const generateCase = (type: string): Promise<SdCase> =>
  post<SdCase>(sd("/cases/generate"), { type });

export const listCases = (type?: string): Promise<SdCase[]> =>
  request<SdCase[]>(sd(`/cases${query({ type })}`));

export const drawCase = (type?: string): Promise<SdCase> =>
  request<SdCase>(sd(`/cases/draw${query({ type })}`));

export const createSdSession = (caseId: number): Promise<SdSession> =>
  post<SdSession>(sd("/sessions"), { case_id: caseId });

export const getSdSession = (id: number): Promise<SdSession> =>
  request<SdSession>(sd(`/sessions/${id}`));

export const listSdSessions = (): Promise<SdSessionSummary[]> =>
  request<SdSessionSummary[]>(sd("/sessions"));

export const postSdMessage = (id: number, content: string, elapsedS: number): Promise<SdSession> =>
  post<SdSession>(sd(`/sessions/${id}/messages`), { content, elapsed_s: elapsedS });

export const requestSdReply = (id: number): Promise<SdSession> =>
  post<SdSession>(sd(`/sessions/${id}/reply`));

export const finishSdSession = (id: number): Promise<SdSession> =>
  post<SdSession>(sd(`/sessions/${id}/finish`));

export const putElapsed = (id: number, elapsedS: number): Promise<void> =>
  request<void>(sd(`/sessions/${id}/elapsed`), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ elapsed_s: elapsedS }),
  });

/** Dernière scène enregistrée, ou null si la session n'a pas encore de schéma. */
export async function getScene(id: number): Promise<StoredScene | null> {
  try {
    return await request<StoredScene>(sd(`/sessions/${id}/scene`));
  } catch (err) {
    if (err instanceof ApiError && err.status === HTTP_NOT_FOUND) return null;
    throw err;
  }
}

export const saveScene = (
  id: number,
  elements: SceneElement[],
  appState: Record<string, unknown>,
  elapsedS: number,
  keepalive = false,
): Promise<SceneVersion> =>
  request<SceneVersion>(sd(`/sessions/${id}/scene`), {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ elements, app_state: appState, elapsed_s: elapsedS }),
    keepalive,
  });

export const listSceneVersions = (id: number): Promise<SceneVersion[]> =>
  request<SceneVersion[]>(sd(`/sessions/${id}/scenes`));

export const getSceneVersion = (id: number, version: number): Promise<StoredScene> =>
  request<StoredScene>(sd(`/sessions/${id}/scenes/${version}`));

/** Correction déjà générée, ou null (session non terminée ou correction pas encore demandée). */
export async function getCorrection(id: number): Promise<CorrectionBundle | null> {
  try {
    return await request<CorrectionBundle>(sd(`/sessions/${id}/correction`));
  } catch (err) {
    if (err instanceof ApiError && err.status === HTTP_NOT_FOUND) return null;
    throw err;
  }
}

/** Génère la correction et la solution de référence (appel IA explicite, mis en cache). */
export const requestCorrection = (id: number): Promise<CorrectionBundle> =>
  post<CorrectionBundle>(sd(`/sessions/${id}/correction`));
