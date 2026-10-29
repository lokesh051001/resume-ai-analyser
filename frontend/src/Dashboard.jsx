import { useState, useEffect } from "react";
import { authFetch } from "./auth.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    authFetch("/dashboard/summary/")
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  if (error) return <p style={{ color: "#d9534f" }}>Could not load the dashboard: {error}</p>;
  if (!data) return <p>Loading...</p>;

  const card = { padding: "10px 16px", background: "#f7f7f7", borderRadius: 8, minWidth: 90, textAlign: "center" };
  const when = (iso) => new Date(iso).toLocaleString();

  return (
    <div>
      <h1>My Job Search</h1>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 24 }}>
        <div style={card}><div style={{ fontSize: 24 }}><b>{data.total}</b></div>Total</div>
        {Object.entries(data.by_status).map(([status, n]) => (
          <div key={status} style={card}>
            <div style={{ fontSize: 24 }}><b>{n}</b></div>
            {status}
          </div>
        ))}
      </div>

      <h2>Upcoming interviews</h2>
      {data.upcoming_interviews.length === 0 && <p>None scheduled.</p>}
      <ul>
        {data.upcoming_interviews.map((i) => (
          <li key={i.id}>{i.company}: {i.role} on {when(i.interview_date)}</li>
        ))}
      </ul>

      <h2>Recent resume analyses</h2>
      {data.recent_analyses.length === 0 && <p>No analyses yet.</p>}
      <ul>
        {data.recent_analyses.map((a) => (
          <li key={a.id}>
            {a.filename}: <b>{a.score}</b>/100 ({when(a.created_at)})
            {a.application ? " (linked to an application)" : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}