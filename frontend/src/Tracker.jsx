import { useState, useEffect, useCallback } from "react";
import { authFetch } from "./auth.js";


const API = "/applications/";
const STATUSES = ["saved", "applied", "assessment", "interview", "offer", "rejected", "withdrawn"];
const EMPTY = {
  company: "", role: "", status: "saved", applied_date: "",
  interview_date: "", url: "", job_description: "", notes: "",
};

function toPayload(form) {
  // Empty date fields must be sent as null, because "" is not a valid date.
  return {
    ...form,
    applied_date: form.applied_date || null,
    interview_date: form.interview_date || null,
  };
}

function fromItem(item) {
  return {
    ...EMPTY,
    ...item,
    applied_date: item.applied_date ?? "",
    interview_date: item.interview_date ? item.interview_date.slice(0, 16) : "",
  };
}

function TrackerForm({ initial, onSaved, onCancel }) {
  const [form, setForm] = useState(fromItem(initial));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const editing = Boolean(initial.id);

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const res = await authFetch(editing ? `${API}${initial.id}/` : API, {
        method: editing ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toPayload(form)),
      });
      const data = await res.json();
      if (!res.ok) {
        const messages = Object.entries(data).map(
          ([field, errs]) => `${field}: ${[].concat(errs).join(" ")}`
        );
        throw new Error(messages.join(" | ") || `Server returned ${res.status}`);
      }
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const row = { display: "block", marginBottom: 8 };
  return (
    <form onSubmit={handleSubmit} style={{ padding: 12, background: "#f7f7f7", borderRadius: 8, marginBottom: 20 }}>
      <h3 style={{ marginTop: 0 }}>{editing ? "Edit application" : "Add application"}</h3>
      <label style={row}>Company <input value={form.company} onChange={set("company")} /></label>
      <label style={row}>Role <input value={form.role} onChange={set("role")} /></label>
      <label style={row}>
        Status{" "}
        <select value={form.status} onChange={set("status")}>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </label>
      <label style={row}>Applied on <input type="date" value={form.applied_date} onChange={set("applied_date")} /></label>
      <label style={row}>Interview <input type="datetime-local" value={form.interview_date} onChange={set("interview_date")} /></label>
      <label style={row}>Job URL <input style={{ width: "60%" }} value={form.url} onChange={set("url")} /></label>
      <label style={row}>
        Job description
        <textarea style={{ width: "100%" }} rows={4} value={form.job_description} onChange={set("job_description")} />
      </label>
      <label style={row}>
        Notes
        <textarea style={{ width: "100%" }} rows={3} value={form.notes} onChange={set("notes")} />
      </label>
      <button type="submit" disabled={busy}>{busy ? "Saving..." : "Save"}</button>{" "}
      <button type="button" onClick={onCancel}>Cancel</button>
      {error && <p style={{ color: "#d9534f" }}>{error}</p>}
    </form>
  );
}

export default function Tracker() {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // null = closed, {} = new, item = edit

  const load = useCallback(async () => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (search) params.set("search", search);
    try {
      const res = await authFetch(`${API}?${params}`);
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      setItems(await res.json());
      setError("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [status, search]);

  useEffect(() => {
    load();
  }, [load]);

  async function changeStatus(item, next) {
    await authFetch(`${API}${item.id}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: next }),
    });
    load();
  }

  async function remove(item) {
    if (!window.confirm(`Delete "${item.role}" at ${item.company}?`)) return;
    await authFetch(`${API}${item.id}/`, { method: "DELETE" });
    load();
  }

  const cell = { padding: "6px 8px", borderBottom: "1px solid #eee", textAlign: "left" };
  return (
    <div>
      <h1>Job Tracker</h1>
      {editing && (
        <TrackerForm
          key={editing.id ?? "new"}
          initial={editing}
          onSaved={() => { setEditing(null); load(); }}
          onCancel={() => setEditing(null)}
        />
      )}
      <p>
        <button onClick={() => setEditing({})}>+ Add application</button>{" "}
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>{" "}
        <input placeholder="Search company or role" value={search} onChange={(e) => setSearch(e.target.value)} />
      </p>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "#d9534f" }}>Could not load applications: {error}</p>}
      {!loading && !error && items.length === 0 && <p>No applications found.</p>}
      {items.length > 0 && (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 14 }}>
            <thead>
              <tr>
                <th style={cell}>Company</th><th style={cell}>Role</th><th style={cell}>Status</th>
                <th style={cell}>Applied</th><th style={cell}>Interview</th><th style={cell}></th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td style={cell}>{item.company}</td>
                  <td style={cell}>{item.url ? <a href={item.url} target="_blank" rel="noreferrer">{item.role}</a> : item.role}</td>
                  <td style={cell}>
                    <select value={item.status} onChange={(e) => changeStatus(item, e.target.value)}>
                      {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td style={cell}>{item.applied_date ?? "-"}</td>
                  <td style={cell}>{item.interview_date ? item.interview_date.slice(0, 16).replace("T", " ") : "-"}</td>
                  <td style={cell}>
                    <button onClick={() => setEditing(item)}>Edit</button>{" "}
                    <button onClick={() => remove(item)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}