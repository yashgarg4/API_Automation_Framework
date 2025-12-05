import { useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function jsonRequest(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const resp = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await resp.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!resp.ok) {
    const detail = data?.detail || `Request failed: ${resp.status}`;
    const error = new Error(detail);
    error.status = resp.status;
    error.data = data;
    throw error;
  }

  return data;
}

function AiDashboard() {
  const [uiUrl, setUiUrl] = useState("http://127.0.0.1:5173");
  const [uiGenCode, setUiGenCode] = useState("");
  const [uiGenSavedPath, setUiGenSavedPath] = useState(null);

  const [generated, setGenerated] = useState([]);
  const [genCount, setGenCount] = useState(0);

  const [execSummary, setExecSummary] = useState(null);
  const [execResults, setExecResults] = useState([]);

  const [analysis, setAnalysis] = useState("");
  const [failures, setFailures] = useState([]);

  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLoadGeneratedTests = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await jsonRequest(
        "/ai/dashboard/generated-tests?max_endpoints=10"
      );
      setGenCount(data.count || 0);
      setGenerated(data.items || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAiTests = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await jsonRequest(
        "/ai/dashboard/execute-tests?max_endpoints=10",
        {
          method: "POST",
        }
      );
      setExecSummary(data.summary);
      setExecResults(data.results || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeFailures = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await jsonRequest("/ai/dashboard/analyze-failures");
      setAnalysis(data.analysis || "");
      setFailures(data.failures || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await jsonRequest(
        "/ai/dashboard/test-runs?limit=10&run_type=ai_executor"
      );
      setHistory(data || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateUiTests = async () => {
    setLoading(true);
    setError(null);
    setUiGenCode("");
    setUiGenSavedPath(null);

    try {
      const data = await jsonRequest("/ai/ui/generate-tests", {
        method: "POST",
        body: JSON.stringify({
          url: uiUrl,
          save: true,
        }),
      });

      setUiGenCode(data.code || "");
      setUiGenSavedPath(data.saved_path || null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-dashboard">
      <h2>AI Testing Dashboard</h2>

      {loading && <p>Loading...</p>}
      {error && <p className="status-error">Error: {error}</p>}

      <div className="ai-dashboard-grid">
        {/* AI UI Test Generator */}
        <section className="ai-card ai-card-wide">
          <h3>AI UI Test Generator (Python Playwright)</h3>
          <p style={{ fontSize: "0.9rem" }}>
            This will inspect the given URL with Playwright on the backend and
            ask Gemini to generate pytest + Playwright tests in Python.
          </p>
          <div
            style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}
          >
            <input
              type="text"
              value={uiUrl}
              onChange={(e) => setUiUrl(e.target.value)}
              style={{ flex: 1 }}
              placeholder="URL to inspect, e.g. http://127.0.0.1:5173"
            />
            <button onClick={handleGenerateUiTests}>Generate UI Tests</button>
          </div>
          {uiGenSavedPath && (
            <p style={{ fontSize: "0.85rem" }}>
              Saved to: <code>{uiGenSavedPath}</code>
            </p>
          )}
          {uiGenCode && (
            <div className="ai-analysis">
              <h4>Generated Python Test File</h4>
              <pre>{uiGenCode}</pre>
            </div>
          )}
        </section>

        {/* Generated tests */}
        <section className="ai-card">
          <h3>AI Generated Test Cases</h3>
          <button onClick={handleLoadGeneratedTests}>
            Load Generated Tests
          </button>
          <p>Count: {genCount}</p>
          <div className="ai-list">
            {generated.slice(0, 10).map((tc, idx) => (
              <div key={idx} className="ai-list-item">
                <strong>{tc.name}</strong>
                <div>
                  {(tc.request?.method || "GET") +
                    " " +
                    (tc.request?.path || "/")}
                </div>
                <div>Category: {tc.category}</div>
              </div>
            ))}
            {generated.length > 10 && (
              <p>Showing first 10 of {generated.length} test cases.</p>
            )}
          </div>
        </section>

        {/* AI test executor */}
        <section className="ai-card">
          <h3>AI Test Executor</h3>
          <button onClick={handleExecuteAiTests}>Run AI-Generated Tests</button>
          {execSummary && (
            <div className="ai-summary">
              <p>Total: {execSummary.total}</p>
              <p>Passed: {execSummary.passed}</p>
              <p>Failed: {execSummary.failed}</p>
              <p>Auth used: {execSummary.used_auth ? "Yes" : "No"}</p>
            </div>
          )}
          <div className="ai-list">
            {execResults.slice(0, 10).map((r) => (
              <div
                key={r.index}
                className={`ai-list-item ${
                  r.passed ? "status-ok" : "status-error"
                }`}
              >
                <strong>{r.name}</strong>
                <div>
                  {r.method} {r.path} →{" "}
                  {r.status_code !== null ? r.status_code : "ERR"}
                </div>
                <div>Category: {r.category}</div>
                {!r.passed && r.error && (
                  <div style={{ fontSize: "0.85rem" }}>Error: {r.error}</div>
                )}
              </div>
            ))}
            {execResults.length > 10 && (
              <p>Showing first 10 of {execResults.length} executions.</p>
            )}
          </div>
        </section>

        {/* Failure analysis */}
        <section className="ai-card ai-card-wide">
          <h3>AI Failure Analyzer (from PyTest JUnit)</h3>
          <button onClick={handleAnalyzeFailures}>
            Analyze Last API Test Failures
          </button>
          <p style={{ fontSize: "0.9rem" }}>
            Make sure you've run:{" "}
            <code>pytest tests/api --junitxml=reports/api-results.xml</code>
          </p>
          {failures && failures.length > 0 && (
            <details>
              <summary>Show raw failures ({failures.length})</summary>
              <ul>
                {failures.map((f, idx) => (
                  <li key={idx}>
                    <strong>{f["test"]}</strong> – {f["type"]} – {f["message"]}
                  </li>
                ))}
              </ul>
            </details>
          )}
          {analysis && (
            <div className="ai-analysis">
              <h4>AI Analysis</h4>
              <pre>{analysis}</pre>
            </div>
          )}
        </section>

        {/* AI test run history */}
        <section className="ai-card ai-card-wide">
          <h3>AI Test Run History</h3>
          <button onClick={handleLoadHistory}>
            Load Last 10 AI Executor Runs
          </button>
          <div className="ai-list">
            {history.length === 0 && <p>No runs loaded yet.</p>}
            {history.map((run) => (
              <div key={run.id} className="ai-list-item">
                <strong>Run #{run.id}</strong> – {run.run_type} –{" "}
                <span
                  className={
                    run.status === "passed"
                      ? "status-ok"
                      : run.status === "failed"
                      ? "status-error"
                      : ""
                  }
                >
                  {run.status}
                </span>
                <div>
                  Started:{" "}
                  {run.started_at
                    ? new Date(run.started_at).toLocaleString()
                    : "N/A"}
                  {run.finished_at && (
                    <>
                      {" | "}Finished:{" "}
                      {new Date(run.finished_at).toLocaleString()}
                    </>
                  )}
                </div>
                {run.summary && (
                  <div style={{ fontSize: "0.85rem", marginTop: "0.25rem" }}>
                    {typeof run.summary.total !== "undefined" && (
                      <>
                        Total: {run.summary.total}, Passed: {run.summary.passed}
                        , Failed: {run.summary.failed}
                      </>
                    )}
                    {run.summary.error && (
                      <span>Error: {run.summary.error}</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default AiDashboard;
