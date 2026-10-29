const API_ROOT = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
const TOKEN_KEY = "resume_ai_token";
const USER_KEY = "resume_ai_user";

export function getSession() {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { token, username: localStorage.getItem(USER_KEY) || "" } : null;
  } catch {
    return null;
  }
}

export function saveSession({ token, username }) {
  try {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
  } catch {
    /* storage unavailable: the user will simply have to log in again */
  }
}

export function clearSession() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {
    /* ignore */
  }
}

// fetch() that adds the login token. A 401 means the token is gone, so we tell the app to show the login screen.
export async function authFetch(path, options = {}) {
  const session = getSession();
  const headers = { ...(options.headers || {}) };
  if (session) headers.Authorization = `Token ${session.token}`;
  const res = await fetch(`${API_ROOT}${path}`, { ...options, headers });
  if (res.status === 401) {
    clearSession();
    window.dispatchEvent(new Event("auth-expired"));
  }
  return res;
}

export async function authenticate(mode, username, password) {
  const res = await fetch(`${API_ROOT}/auth/${mode}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const messages = Object.values(data).flat();
    throw new Error(messages.join(" ") || `Server returned ${res.status}`);
  }
  return data;
}