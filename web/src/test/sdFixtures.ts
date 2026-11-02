import type { CaseType, SdSession, SdSessionSummary, StoredScene } from "../types";

export const CASE_TYPES: CaseType[] = [
  { slug: "rag", titre: "RAG sur une grande base documentaire", description: "Questions sur un corpus." },
  { slug: "agent", titre: "Agent ou assistant avec outils", description: "Un assistant qui agit." },
];

export const SD_SESSION: SdSession = {
  id: 5,
  created_at: "2026-11-02T10:00:00+00:00",
  statut: "en_cours",
  elapsed_s: 600,
  case: {
    id: 3,
    type: "rag",
    titre: "Assistant documentaire interne",
    brief: "Une équipe veut un assistant sur sa documentation.",
    nb_sessions: 1,
  },
  messages: [
    {
      id: 1,
      role: "assistant",
      content: "Une équipe veut un assistant sur sa documentation. Pose-moi tes questions.",
      created_at: "t0",
    },
  ],
  user_messages: 0,
  max_user_messages: 40,
  awaiting_reply: false,
};

export const AWAITING: SdSession = {
  ...SD_SESSION,
  user_messages: 1,
  awaiting_reply: true,
  messages: [
    ...SD_SESSION.messages,
    { id: 2, role: "user", content: "Quel volume de documents ?", created_at: "t1" },
  ],
};

export const ANSWERED: SdSession = {
  ...AWAITING,
  awaiting_reply: false,
  messages: [
    ...AWAITING.messages,
    { id: 3, role: "assistant", content: "Environ douze millions de pages.", created_at: "t2" },
  ],
};

export const FINISHED_SD: SdSession = { ...ANSWERED, statut: "terminee" };

export const STORED_SCENE: StoredScene = {
  version: 2,
  created_at: "2026-11-02T10:30:00+00:00",
  elements: [
    { id: "a", type: "rectangle", version: 3, isDeleted: false, x: 0, y: 0 },
    { id: "b", type: "ellipse", version: 1, isDeleted: false, x: 200, y: 0 },
  ],
  app_state: { viewBackgroundColor: "#ffffff" },
};

export const SD_SUMMARY: SdSessionSummary = {
  id: 5,
  created_at: "2026-11-02T10:00:00+00:00",
  statut: "en_cours",
  type: "rag",
  titre: "Assistant documentaire interne",
  nb_messages: 3,
  elapsed_s: 600,
};
