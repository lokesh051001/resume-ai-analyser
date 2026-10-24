import { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000/api";

const DEFAULT_WEIGHTS = {
  required_skills: 40,
  preferred_skills: 10,
  semantic: 20,
  evidence: 15,
  completeness: 15,
};

function recalc(breakdown, weights) {
  const keys = Object.keys(breakdown);
  const total = keys.reduce((s, k) => s + (weights[k] ?? 0), 0);
  if (total === 0) return 0;
  const sum = keys.reduce((s, k) => s + (weights[k] ?? 0) * breakdown[k], 0);
  return Math.round((sum / total) * 10) / 10;
}

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
  const semantic = r.semantic ?? [];
  return (
    <li style={{ marginBottom: 20, listStyle: "none" }}>
      <div>
        {a.filename}: <b>{score}</b>/100
        {score !== a.score && (
          <span style={{ color: "#888", fontSize: 12 }}> (saved: {a.score})</span>
        )}
      </div>
      <ScoreBar value={score} />
      <div style={{ fontSize: 13, color: "#555", marginTop: 4 }}>
        {Object.entries(r.breakdown).map(([k, v]) => `${k}: ${v}`).join(" · ")}
      </div>
      <div style={{ fontSize: 13, color: "#555" }}>
        Required missing: {r.required_missing.join(", ") || "none"}
      </div>
      <div style={{ fontSize: 13, color: "#555" }}>
        Listed but not demonstrated: {r.not_demonstrated.join(", ") || "none"}
      </div>

      {semantic.length > 0 && (
        <details style={{ fontSize: 13, marginTop: 6 }}>
          <summary>
            Requirement matches ({semantic.filter((m) => m.met).length}/{semantic.length})
          </summary>
          <ul style={{ paddingLeft: 18 }}>
            {semantic.map((m, i) => (
              <li key={i} style={{ marginBottom: 4 }}>
                {m.met ? "✓" : "✗"} {m.requirement}{" "}
                <span style={{ color: "#888" }}>(similarity {m.score})</span>
                {m.met && m.evidence && (
                  <div style={{ color: "#555" }}>
                    Closest passage ({m.evidence_section}): {m.evidence}
                  </div>
                )}
              </li>
            ))}
          </ul>
          <div style={{ color: "#888" }}>
            Similarity shows related wording, not proof of the skill.
          </div>
        </details>
      )}
    </li>
  );
}

function UploadForm({ onCreated }) {
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [twoColumn, setTwoColumn] = useState(false);
  const [requestSuggestions, setRequestSuggestions] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [suggestionError, setSuggestionError] = useState("");
  const [suggestions, setSuggestions] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuggestionError("");
    setSuggestions(null);
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
      if (requestSuggestions) {
        const suggestionBody = new FormData();
        suggestionBody.append("resume", file);
        suggestionBody.append("job_description", job);
        if (twoColumn) suggestionBody.append("two_column", "true");
        try {
          const suggestionRes = await fetch(`${API}/suggestions/`, { method: "POST", body: suggestionBody });
          const suggestionData = await suggestionRes.json();
          if (!suggestionRes.ok) throw new Error(suggestionData.error || "Could not generate suggestions.");
          setSuggestions(suggestionData);
        } catch (err) {
          setSuggestionError(err.message);
        }
      }
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
        <label>
          <input
            type="checkbox"
            checked={requestSuggestions}
            onChange={(e) => setRequestSuggestions(e.target.checked)}
          />{" "}
          Send relevant resume text to Claude for draft wording suggestions
        </label>
      </p>
      <p style={{ color: "#666", fontSize: 13 }}>
        Optional. Suggestions are requested only when selected. The PDF is not saved by this feature;
        experience, project, and summary text is sent to Anthropic for this request.
      </p>
      <p>
        <button type="submit" disabled={busy}>
          {busy ? "Analysing..." : "Analyse"}
        </button>
      </p>
      {error && <p style={{ color: "#d9534f" }}>{error}</p>}
      {suggestionError && <p style={{ color: "#d9534f" }}>Analysis completed. {suggestionError}</p>}
      {suggestions && (
        <section style={{ background: "#f7f7f7", padding: 16, borderRadius: 8 }}>
          <h3>Draft suggestions</h3>
          <p>{suggestions.draft_notice}</p>
          {suggestions.suggestions.length === 0 && <p>No wording suggestions were returned.</p>}
          {suggestions.suggestions.map((item, i) => (
            <article key={i} style={{ marginBottom: 16 }}>
              <p><b>Original:</b> {item.original}</p>
              <p><b>Draft:</b> {item.suggested_rewrite}</p>
              <p><b>Why:</b> {item.reason}</p>
              {item.question && <p><b>Question for you:</b> {item.question}</p>}
            </article>
          ))}
        </section>
      )}
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
      <WeightSliders weights={weights} onChange={setWeights} />
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
