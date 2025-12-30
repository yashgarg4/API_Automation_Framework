import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../apiClient";

function ProjectsPanel({ token, selectedProject, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const loadProjects = async () => {
    if (!token) return;
    try {
      setError(null);
      const data = await apiGet("/projects/", { headers: authHeaders });
      setProjects(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    loadProjects();
  }, [token]);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!token) return;
    try {
      setError(null);
      await apiPost(
        "/projects/",
        { name, description },
        { headers: authHeaders }
      );
      setName("");
      setDescription("");
      await loadProjects();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSelect = (project) => {
    onSelectProject(project);
  };

  return (
    <div>
      {!token && <p>Please login to manage projects.</p>}

      {token && (
        <>
          <form onSubmit={handleCreateProject}>
            <label>
              Project name
              <input
                data-testid="project-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </label>
            <label>
              Description
              <input
                data-testid="project-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </label>
            <button data-testid="create-project-button" type="submit">
              Create Project
            </button>
          </form>

          <button
            type="button"
            data-testid="load-projects-button"
            onClick={loadProjects}
          >
            Refresh Projects
          </button>

          {error && <p className="status-error">{error}</p>}

          <ul>
            {projects.map((p) => (
              <li
                key={p.id}
                data-testid="project-item"
                onClick={() => handleSelect(p)}
                style={{
                  cursor: "pointer",
                  fontWeight: selectedProject?.id === p.id ? "bold" : "normal",
                }}
              >
                {p.name} (ID {p.id})
              </li>
            ))}
          </ul>

          <p data-testid="current-project-name">
            Selected:{" "}
            {selectedProject
              ? `${selectedProject.name} (ID ${selectedProject.id})`
              : "None"}
          </p>
        </>
      )}
    </div>
  );
}

export default ProjectsPanel;
