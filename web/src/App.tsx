import { lazy, Suspense } from "react";
import { Navigate, NavLink, Route, Routes, useMatch } from "react-router-dom";
import LanguageToggle from "./components/LanguageToggle";
import ThemeToggle from "./components/ThemeToggle";
import { type TKey, useI18n } from "./i18n";
import Consommation from "./pages/Consommation";
import Cours from "./pages/Cours";
import CoursTheme from "./pages/CoursTheme";
import EntretienManager from "./pages/EntretienManager";
import Historique from "./pages/Historique";
import ManagerSession from "./pages/ManagerSession";
import Revision from "./pages/Revision";
import SystemDesign from "./pages/SystemDesign";
import Workflows from "./pages/Workflows";
import WorkflowsRevision from "./pages/WorkflowsRevision";
import WorkflowsTheme from "./pages/WorkflowsTheme";

// Excalidraw est lourd : chargé uniquement quand on ouvre une session de System Design.
const SystemDesignSession = lazy(() => import("./pages/SystemDesignSession"));

const NAV_ITEMS: { to: string; label: TKey }[] = [
  { to: "/cours", label: "app.nav.courses" },
  { to: "/workflows", label: "app.nav.workflows" },
  { to: "/entretien-manager", label: "app.nav.manager" },
  { to: "/system-design", label: "app.nav.sd" },
  { to: "/historique", label: "app.nav.history" },
  { to: "/consommation", label: "app.nav.usage" },
];

export default function App() {
  const { t } = useI18n();
  const wide = useMatch("/system-design/sessions/:id") !== null;
  return (
    <div className="layout">
      <header className="topbar">
        <span className="brand">Prépa Mistral</span>
        <nav className="nav" aria-label={t("app.navLabel")}>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} className="nav-link">
              {t(item.label)}
            </NavLink>
          ))}
        </nav>
        <LanguageToggle />
        <ThemeToggle />
      </header>
      <main className={wide ? "content content-wide" : "content"}>
        <Routes>
          <Route path="/" element={<Navigate to="/cours" replace />} />
          <Route path="/cours" element={<Cours />} />
          <Route path="/cours/revision" element={<Revision />} />
          <Route path="/cours/:slug" element={<CoursTheme />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/workflows/revision" element={<WorkflowsRevision />} />
          <Route path="/workflows/:slug" element={<WorkflowsTheme />} />
          <Route path="/entretien-manager" element={<EntretienManager />} />
          <Route path="/entretien-manager/sessions/:id" element={<ManagerSession />} />
          <Route path="/system-design" element={<SystemDesign />} />
          <Route
            path="/system-design/sessions/:id"
            element={
              <Suspense fallback={<p className="muted">{t("app.editorLoading")}</p>}>
                <SystemDesignSession />
              </Suspense>
            }
          />
          <Route path="/historique" element={<Historique />} />
          <Route path="/consommation" element={<Consommation />} />
        </Routes>
      </main>
    </div>
  );
}
