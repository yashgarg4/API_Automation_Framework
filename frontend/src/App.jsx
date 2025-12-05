import { useState } from "react";
import "./App.css";

import AuthSection from "./components/AuthSection";
import ProjectsPanel from "./components/ProjectsPanel";
import BugsPanel from "./components/BugsPanel";
import AiDashboard from "./components/AiDashboard";

function App() {
  const [token, setToken] = useState(null);
  const [currentUserEmail, setCurrentUserEmail] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  const handleLoginSuccess = (accessToken, email) => {
    setToken(accessToken);
    setCurrentUserEmail(email);
  };

  const handleLogout = () => {
    setToken(null);
    setCurrentUserEmail(null);
    setSelectedProject(null);
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <h1>TestHub – React Frontend</h1>
        {currentUserEmail ? (
          <div className="user-info">
            <span>Logged in as: {currentUserEmail}</span>
            <button onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <span>Not logged in</span>
        )}
      </header>

      <main className="app-main">
        <section className="app-section">
          <h2>Auth</h2>
          <AuthSection onLoginSuccess={handleLoginSuccess} />
        </section>

        <section className="app-section">
          <h2>Projects</h2>
          <ProjectsPanel
            token={token}
            selectedProject={selectedProject}
            onSelectProject={setSelectedProject}
          />
        </section>

        <section className="app-section">
          <h2>Bugs</h2>
          <BugsPanel token={token} selectedProject={selectedProject} />
        </section>

        <section className="app-section">
          <AiDashboard />
        </section>
      </main>
    </div>
  );
}

export default App;
