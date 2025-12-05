import { useState } from "react";
import { apiPost } from "../apiClient";

function AuthSection({ onLoginSuccess }) {
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerFullName, setRegisterFullName] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [registerStatus, setRegisterStatus] = useState(null);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [loginStatus, setLoginStatus] = useState(null);

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await apiPost("/auth/register", {
        email: registerEmail,
        full_name: registerFullName,
        password: registerPassword,
      });
      setRegisterStatus({
        type: "success",
        message: "Registered successfully",
      });
    } catch (err) {
      setRegisterStatus({ type: "error", message: err.message });
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // OAuth2 form-encoded login – we’ll manually handle here
      const baseUrl =
        import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      const body = new URLSearchParams();
      body.append("username", loginEmail);
      body.append("password", loginPassword);

      const resp = await fetch(`${baseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });

      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || "Login failed");
      }

      setLoginStatus({ type: "success", message: "Login successful" });
      onLoginSuccess(data.access_token, loginEmail);
    } catch (err) {
      setLoginStatus({ type: "error", message: err.message });
    }
  };

  return (
    <div className="auth-section">
      <div className="auth-block">
        <h3>Register</h3>
        <form onSubmit={handleRegister}>
          <label>
            Email
            <input
              data-testid="register-email"
              type="email"
              value={registerEmail}
              onChange={(e) => setRegisterEmail(e.target.value)}
              required
            />
          </label>
          <label>
            Full Name
            <input
              data-testid="register-fullname"
              type="text"
              value={registerFullName}
              onChange={(e) => setRegisterFullName(e.target.value)}
            />
          </label>
          <label>
            Password
            <input
              data-testid="register-password"
              type="password"
              value={registerPassword}
              onChange={(e) => setRegisterPassword(e.target.value)}
              required
            />
          </label>
          <button data-testid="register-button" type="submit">
            Register
          </button>
        </form>
        {registerStatus && (
          <p
            className={
              registerStatus.type === "success" ? "status-ok" : "status-error"
            }
          >
            {registerStatus.message}
          </p>
        )}
      </div>

      <div className="auth-block">
        <h3>Login</h3>
        <form onSubmit={handleLogin}>
          <label>
            Email
            <input
              data-testid="login-email"
              type="email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              data-testid="login-password"
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
              required
            />
          </label>
          <button data-testid="login-button" type="submit">
            Login
          </button>
        </form>
        {loginStatus && (
          <p
            className={
              loginStatus.type === "success" ? "status-ok" : "status-error"
            }
          >
            {loginStatus.message}
          </p>
        )}
      </div>
    </div>
  );
}

export default AuthSection;
