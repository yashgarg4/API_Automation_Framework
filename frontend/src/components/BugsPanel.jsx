import { useEffect, useState } from "react";
import { apiGet, apiPost, apiPatch } from "../apiClient";

function BugsPanel({ token, selectedProject }) {
  const [bugs, setBugs] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity] = useState("medium");
  const [priority, setPriority] = useState("medium");
  const [error, setError] = useState(null);

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  const loadBugs = async () => {
    if (!token || !selectedProject) return;
    try {
      setError(null);
      const data = await apiGet(`/projects/${selectedProject.id}/bugs`, {
        headers: authHeaders,
      });
      setBugs(data);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    setBugs([]);
    if (selectedProject && token) {
      loadBugs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProject, token]);

  const handleCreateBug = async (e) => {
    e.preventDefault();
    if (!token || !selectedProject) return;
    try {
      setError(null);
      await apiPost(
        `/projects/${selectedProject.id}/bugs`,
        {
          title,
          description,
          severity,
          priority,
          assignee_id: null,
        },
        { headers: authHeaders }
      );
      setTitle("");
      setDescription("");
      setSeverity("medium");
      setPriority("medium");
      await loadBugs();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStatusChange = async (bugId, newStatus) => {
    try {
      setError(null);
      await apiPatch(
        `/bugs/${bugId}/status`,
        { status: newStatus },
        { headers: authHeaders }
      );
      await loadBugs();
    } catch (err) {
      setError(err.message);
    }
  };

  if (!token) {
    return <p>Please login to manage bugs.</p>;
  }

  if (!selectedProject) {
    return <p>Please select a project to view bugs.</p>;
  }

  return (
    <div>
      <form onSubmit={handleCreateBug}>
        <label>
          Title
          <input
            data-testid="bug-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </label>
        <label>
          Description
          <textarea
            data-testid="bug-description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </label>
        <label>
          Severity
          <select
            data-testid="bug-severity"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
            <option value="critical">critical</option>
          </select>
        </label>
        <label>
          Priority
          <select
            data-testid="bug-priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>
        <button data-testid="create-bug-button" type="submit">
          Create Bug
        </button>
      </form>

      <button type="button" data-testid="load-bugs-button" onClick={loadBugs}>
        Refresh Bugs
      </button>

      {error && <p className="status-error">{error}</p>}

      <ul>
        {bugs.map((b) => (
          <li key={b.id} data-testid="bug-item">
            <strong>{b.title}</strong> – status: {b.status} – severity:{" "}
            {b.severity}
            <div>
              {/* Simple status change buttons for demo */}
              <button onClick={() => handleStatusChange(b.id, "in_progress")}>
                In Progress
              </button>
              <button onClick={() => handleStatusChange(b.id, "resolved")}>
                Resolved
              </button>
              <button onClick={() => handleStatusChange(b.id, "closed")}>
                Closed
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default BugsPanel;
