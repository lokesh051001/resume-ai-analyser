import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000/api";

export default function App() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/analyses/`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then((data) => setAnalyses(data.analyses))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Could not load analyses: {error}</p>;

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Resume Analyser</h1>
      {analyses.length === 0 && <p>No analyses yet.</p>}
      <ul>
        {analyses.map((a) => (
          <li key={a.id}>
            {a.filename}: <b>{a.score}</b>
            <div style={{ fontSize: 13, color: "#555" }}>
              Missing: {a.result.required_missing.join(", ") || "none"}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}