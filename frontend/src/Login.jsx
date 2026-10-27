import { useState } from "react";
import { authenticate } from "./auth.js";

export default function Login({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      onLoggedIn(await authenticate(mode, username, password));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 320, marginTop: 24 }}>
      <h2>{mode === "login" ? "Log in" : "Create account"}</h2>
      <p>
        <label>
          Username <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </label>
      </p>
      <p>
        <label>
          Password{" "}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
        </label>
      </p>
      <button type="submit" disabled={busy}>{busy ? "Please wait..." : mode === "login" ? "Log in" : "Register"}</button>{" "}
      <button type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
        {mode === "login" ? "Need an account?" : "Have an account?"}
      </button>
      {error && <p style={{ color: "#d9534f" }}>{error}</p>}
    </form>
  );
}