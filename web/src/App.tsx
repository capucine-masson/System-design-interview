import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import ThemeToggle from "./components/ThemeToggle";
import Consommation from "./pages/Consommation";
import Cours from "./pages/Cours";
import CoursTheme from "./pages/CoursTheme";
import EntretienManager from "./pages/EntretienManager";
import Historique from "./pages/Historique";
import ManagerSession from "./pages/ManagerSession";
import Revision from "./pages/Revision";
import SystemDesign from "./pages/SystemDesign";

const NAV_ITEMS = [
  { to: "/cours", label: "Cours" },
  { to: "/entretien-manager", label: "Entretien manager" },
  { to: "/system-design", label: "System Design" },
  { to: "/historique", label: "Historique" },
  { to: "/consommation", label: "Consommation" },
];

export default function App() {
  return (
    <div className="layout">
      <header className="topbar">
        <span className="brand">Prépa Mistral</span>
        <nav className="nav" aria-label="Navigation principale">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} className="nav-link">
              {item.label}
            </NavLink>
          ))}
        </nav>
        <ThemeToggle />
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/cours" replace />} />
          <Route path="/cours" element={<Cours />} />
          <Route path="/cours/revision" element={<Revision />} />
          <Route path="/cours/:slug" element={<CoursTheme />} />
          <Route path="/entretien-manager" element={<EntretienManager />} />
          <Route path="/entretien-manager/sessions/:id" element={<ManagerSession />} />
          <Route path="/system-design" element={<SystemDesign />} />
          <Route path="/historique" element={<Historique />} />
          <Route path="/consommation" element={<Consommation />} />
        </Routes>
      </main>
    </div>
  );
}
