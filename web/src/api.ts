import type {
  Card,
  Categorie,
  Difficulte,
  Question,
  Session,
  SessionSummary,
  Statut,
  Theme,
  UsageSummary,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL;
const HTTP_NO_CONTENT = 204;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new Error("API injoignable : le backend est-il lancé ?");
  }
  if (!response.ok) {
    const body: { detail?: string } = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : `Erreur ${response.status}`);
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

export const getCards = (slug: string, statut?: Statut): Promise<Card[]> =>
  request<Card[]>(`/api/themes/${encodeURIComponent(slug)}/cards${query({ statut })}`);

export const getRandomCard = (options: {
  theme?: string;
  statut?: Statut;
  exclude?: number;
}): Promise<Card> => request<Card>(`/api/cards/random${query(options)}`);

export const setProgress = (cardId: number, statut: Statut | null): Promise<void> =>
  request<void>(`/api/cards/${cardId}/progress`, {
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
