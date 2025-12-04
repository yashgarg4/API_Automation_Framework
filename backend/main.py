from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from backend.core.config import get_settings
from backend.db.session import Base, engine

# Import models so they are registered
from backend.models import user  # noqa: F401
from backend.models import project  # noqa: F401
from backend.models import bug  # noqa: F401

# Routers
from backend.api.routes import auth as auth_routes
from backend.api.routes import users as user_routes  # NEW
from backend.api.routes import projects as project_routes  # NEW
from backend.api.routes import bugs as bug_routes  # NEW
from backend.api.routes import ai_tests as ai_tests_routes  # NEW

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

APP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>TestHub UI</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 20px;
    }
    h2 {
      margin-top: 24px;
    }
    .section {
      border: 1px solid #ddd;
      padding: 12px;
      margin-bottom: 16px;
      border-radius: 6px;
    }
    label {
      display: block;
      margin-top: 6px;
    }
    input, select, button, textarea {
      margin-top: 4px;
      padding: 4px;
    }
    ul {
      padding-left: 18px;
    }
    .project-item {
      cursor: pointer;
      padding: 2px 4px;
    }
    .project-item:hover {
      background-color: #f0f0f0;
    }
    .status-ok {
      color: green;
    }
    .status-error {
      color: red;
    }
    #current-project {
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>TestHub – Demo UI</h1>

  <div class="section">
    <h2>Health</h2>
    <button id="btn-health" onclick="checkHealth()" data-testid="health-button">Check Health</button>
    <span id="health-status"></span>
  </div>

  <div class="section">
    <h2>Register</h2>
    <label>Email
      <input id="reg-email" type="email" data-testid="register-email" />
    </label>
    <label>Full Name
      <input id="reg-fullname" type="text" data-testid="register-fullname" />
    </label>
    <label>Password
      <input id="reg-password" type="password" data-testid="register-password" />
    </label>
    <button onclick="registerUser()" data-testid="register-button">Register</button>
    <div id="register-status"></div>
  </div>

  <div class="section">
    <h2>Login</h2>
    <label>Email
      <input id="login-email" type="email" data-testid="login-email" />
    </label>
    <label>Password
      <input id="login-password" type="password" data-testid="login-password" />
    </label>
    <button onclick="loginUser()" data-testid="login-button">Login</button>
    <div id="login-status"></div>
    <div id="logged-in-user"></div>
  </div>

  <div class="section">
    <h2>Projects</h2>
    <p>Current user projects:</p>
    <button onclick="loadProjects()" data-testid="load-projects-button">Load Projects</button>
    <ul id="projects-list"></ul>

    <h3>Create Project</h3>
    <label>Name
      <input id="project-name" type="text" data-testid="project-name" />
    </label>
    <label>Description
      <input id="project-description" type="text" data-testid="project-description" />
    </label>
    <button onclick="createProject()" data-testid="create-project-button">Create Project</button>

    <p>Selected project: <span id="current-project" data-testid="current-project-name">None</span></p>
  </div>

  <div class="section">
    <h2>Bugs for Selected Project</h2>
    <button onclick="loadBugs()" data-testid="load-bugs-button">Load Bugs</button>
    <ul id="bugs-list"></ul>

    <h3>Create Bug</h3>
    <label>Title
      <input id="bug-title" type="text" data-testid="bug-title" />
    </label>
    <label>Description
      <textarea id="bug-description" data-testid="bug-description"></textarea>
    </label>
    <label>Severity
      <select id="bug-severity" data-testid="bug-severity">
        <option value="low">low</option>
        <option value="medium" selected>medium</option>
        <option value="high">high</option>
        <option value="critical">critical</option>
      </select>
    </label>
    <label>Priority
      <select id="bug-priority" data-testid="bug-priority">
        <option value="low">low</option>
        <option value="medium" selected>medium</option>
        <option value="high">high</option>
      </select>
    </label>
    <button onclick="createBug()" data-testid="create-bug-button">Create Bug</button>
  </div>

  <script>
    let token = null;
    let currentProjectId = null;

    function setStatus(id, message, ok=true) {
      const el = document.getElementById(id);
      el.textContent = message;
      el.className = ok ? "status-ok" : "status-error";
    }

    async function checkHealth() {
      try {
        const res = await fetch("/health");
        if (!res.ok) throw new Error("Health failed");
        const data = await res.json();
        setStatus("health-status", "OK: " + JSON.stringify(data), true);
      } catch (e) {
        setStatus("health-status", "ERROR: " + e.message, false);
      }
    }

    async function registerUser() {
      const email = document.getElementById("reg-email").value;
      const fullname = document.getElementById("reg-fullname").value;
      const password = document.getElementById("reg-password").value;

      try {
        const res = await fetch("/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, full_name: fullname, password })
        });
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt);
        }
        const data = await res.json();
        setStatus("register-status", "Registered: " + data.email, true);
      } catch (e) {
        setStatus("register-status", "Register error: " + e.message, false);
      }
    }

    async function loginUser() {
      const email = document.getElementById("login-email").value;
      const password = document.getElementById("login-password").value;

      try {
        const body = new URLSearchParams();
        body.append("username", email);
        body.append("password", password);

        const res = await fetch("/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body
        });
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(txt);
        }
        const data = await res.json();
        token = data.access_token;
        setStatus("login-status", "Login successful", true);
        const userDiv = document.getElementById("logged-in-user");
        userDiv.textContent = "Logged in as: " + email;
        userDiv.dataset.email = email;
      } catch (e) {
        token = null;
        setStatus("login-status", "Login error: " + e.message, false);
        document.getElementById("logged-in-user").textContent = "";
      }
    }

    function getAuthHeaders() {
      if (!token) {
        throw new Error("Not logged in");
      }
      return { "Authorization": "Bearer " + token, "Content-Type": "application/json" };
    }

    async function loadProjects() {
      try {
        const headers = getAuthHeaders();
        const res = await fetch("/projects/", { headers });
        if (!res.ok) throw new Error(await res.text());
        const projects = await res.json();
        const list = document.getElementById("projects-list");
        list.innerHTML = "";
        projects.forEach(p => {
          const li = document.createElement("li");
          li.textContent = p.name;
          li.className = "project-item";
          li.dataset.projectId = p.id;
          li.setAttribute("data-testid", "project-item");
          li.onclick = () => selectProject(p.id, p.name);
          list.appendChild(li);
        });
      } catch (e) {
        alert("Error loading projects: " + e.message);
      }
    }

    function selectProject(id, name) {
      currentProjectId = id;
      const el = document.getElementById("current-project");
      el.textContent = name + " (ID " + id + ")";
      el.dataset.projectId = id;
    }

    async function createProject() {
      const name = document.getElementById("project-name").value;
      const description = document.getElementById("project-description").value;
      try {
        const headers = getAuthHeaders();
        const res = await fetch("/projects/", {
          method: "POST",
          headers,
          body: JSON.stringify({ name, description })
        });
        if (!res.ok) throw new Error(await res.text());
        await loadProjects();
      } catch (e) {
        alert("Error creating project: " + e.message);
      }
    }

    async function loadBugs() {
      if (!currentProjectId) {
        alert("Select a project first");
        return;
      }
      try {
        const headers = getAuthHeaders();
        const res = await fetch(`/projects/${currentProjectId}/bugs`, { headers });
        if (!res.ok) throw new Error(await res.text());
        const bugs = await res.json();
        const list = document.getElementById("bugs-list");
        list.innerHTML = "";
        bugs.forEach(b => {
          const li = document.createElement("li");
          li.setAttribute("data-testid", "bug-item");
          li.dataset.bugId = b.id;
          li.textContent = `${b.title} [status: ${b.status}]`;
          list.appendChild(li);
        });
      } catch (e) {
        alert("Error loading bugs: " + e.message);
      }
    }

    async function createBug() {
      if (!currentProjectId) {
        alert("Select a project first");
        return;
      }
      const title = document.getElementById("bug-title").value;
      const description = document.getElementById("bug-description").value;
      const severity = document.getElementById("bug-severity").value;
      const priority = document.getElementById("bug-priority").value;

      try {
        const headers = getAuthHeaders();
        const res = await fetch(`/projects/${currentProjectId}/bugs`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            title,
            description,
            severity,
            priority,
            assignee_id: null
          })
        });
        if (!res.ok) throw new Error(await res.text());
        await loadBugs();
      } catch (e) {
        alert("Error creating bug: " + e.message);
      }
    }
  </script>
</body>
</html>
"""


@app.get("/app", response_class=HTMLResponse, tags=["ui"])
def app_ui():
    return HTMLResponse(content=APP_HTML)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)  
app.include_router(project_routes.router) 
app.include_router(bug_routes.router) 
app.include_router(ai_tests_routes.router)  # NEW