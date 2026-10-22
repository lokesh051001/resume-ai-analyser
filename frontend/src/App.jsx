import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000/api";

function ScoreBar({ value }) {
  const color = value >= 75 ? "#2e9e5b" : value >= 50 ? "#e0a800" : "#d9534f";
  return (
    <div style={{ background: "#eee", borderRadius: 6, height: 12, width: "100%" }}>
      <div
        style={{
          width: `${Math.min(value, 100)}%`,
          background: color,
          height: "100%",
          borderRadius: 6,
          transition: "width 0.4s",
        }}
      />
    </div>
  );
}
const DEFAULT_WEIGHTS = {
  required_skills: 50,
  preferred_skills: 15,
  evidence: 15,
  completeness: 20,
};

function recalc(breakdown, weights) {
  const keys = Object.keys(breakdown);
  const total = keys.reduce((s, k) => s + (weights[k] ?? 0), 0);
  if (total === 0) return 0;
  const sum = keys.reduce((s, k) => s + (weights[k] ?? 0) * breakdown[k], 0);
  return Math.round((sum / total) * 10) / 10;
}

function WeightSliders({ weights, onChange }) {
  return (
    <div style={{ marginBottom: 24, padding: 12, background: "#f7f7f7", borderRadius: 8 }}>
      <h2 style={{ marginTop: 0 }}>Score weights</h2>
      {Object.entries(weights).map(([k, v]) => (
        <div key={k} style={{ marginBottom: 6 }}>
          <label style={{ display: "inline-block", width: 160 }}>{k}</label>
          <input
            type="range"
            min="0"
            max="100"
            value={v}
            onChange={(e) => onChange({ ...weights, [k]: Number(e.target.value) })}
          />{" "}
          {v}
        </div>
      ))}
      <button onClick={() => onChange(DEFAULT_WEIGHTS)}>Reset</button>
    </div>
  );
}

function AnalysisCard({ a, weights }) {
  const r = a.result;
  const score = recalc(r.breakdown, weights);
  return (
    <li style={{ marginBottom: 20, listStyle: "none" }}>
      <div>
        {a.filename}: <b>{score}</b>/100
        {score !== a.score && (
          <span style={{ color: "#888", fontSize: 12 }}> (saved: {a.score})</span>
        )}
      </div>
      <ScoreBar value={score} />
      {/* ...the rest of the card stays the same... */}
    </li>
  );
}

function UploadForm({ onCreated }) {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [twoColumn, setTwoColumn] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    if (!file) return setError("Please choose a PDF.");

    const body = new FormData();
    body.append("resume", file);
    body.append("job_description", job);
    if (twoColumn) body.append("two_column", "true");

    setBusy(true);
    try {
      // No Content-Type header: the browser adds it, including the multipart boundary.
      const res = await fetch(`${API}/analyse/`, { method: "POST", body });
      const data = await res.json();
      if (!res.ok) {
        const messages = Object.values(data.errors || {}).flat();
        throw new Error(messages.join(" ") || `Server returned ${res.status}`);
      }
      onCreated(data);
      setFile(null);
      e.target.reset();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 32 }}>
      <h2>New analysis</h2>
      <p>
        <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files[0])} />
      </p>
      <p>
        <textarea
          rows={6}
          style={{ width: "100%" }}
          placeholder="Paste the job description..."
          value={job}
          onChange={(e) => setJob(e.target.value)}
        />
      </p>
      <label>
        <input
          type="checkbox"
          checked={twoColumn}
          onChange={(e) => setTwoColumn(e.target.checked)}
        />{" "}
        Resume has two columns
      </label>
      <p>
        <button type="submit" disabled={busy}>
          {busy ? "Analysing..." : "Analyse"}
        </button>
      </p>
      {error && <p style={{ color: "#d9534f" }}>{error}</p>}
    </form>
  );
}

export default function App() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);

  useEffect(() => {
    fetch(`${API}/analyses/`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        return res.json();
      })
      .then((data) => setAnalyses(data.analyses ?? []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ maxWidth: 700, margin: "2rem auto", fontFamily: "sans-serif" }}>
      <h1>Resume Analyser</h1>
      <UploadForm onCreated={(a) => setAnalyses((prev) => [a, ...prev])} />
      <h2>History</h2>
      <WeightSliders weights={weights} onChange={setWeights}/>
      {loading && <p>Loading...</p>}
      {error && <p>Could not load analyses: {error}</p>}
      {!loading && !error && analyses.length === 0 && <p>No analyses yet.</p>}
      <ul style={{ padding: 0 }}>
        {analyses.map((a) => (
          <AnalysisCard key={a.id} a={a} weights={weights} />
        ))}
      </ul>
    </div>
  );
}