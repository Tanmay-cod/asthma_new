"use client";
import { useState } from "react";

export default function Dashboard() {
  const [token, setToken] = useState("");
  const [report, setReport] = useState<any>(null);
  const [err, setErr] = useState("");

  async function gen() {
    setErr("");
    try {
      const res = await fetch("http://localhost:8000/api/v1/reports/personalized", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      setReport(await res.json());
    } catch (e: any) {
      setErr(e.message);
    }
  }

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Personalized PEF Risk</h1>
      <input className="border p-2 w-full" placeholder="Bearer token" value={token} onChange={e => setToken(e.target.value)} />
      <button onClick={gen} className="px-4 py-2 bg-blue-600 text-white rounded">Generate Personalized Report</button>
      {err && <p className="text-red-600">{err}</p>}
      {report && (
        <div className="border rounded p-4 space-y-2">
          <h2 className="text-xl font-semibold">7-Day PEF Deterioration Risk</h2>
          <p className="text-4xl font-bold">{report.model_prediction?.risk_probability != null ? `${(report.model_prediction.risk_probability * 100).toFixed(0)}%` : "N/A"}</p>
          <pre className="text-xs whitespace-pre-wrap max-h-96 overflow-auto">{JSON.stringify(report, null, 2)}</pre>
          <p className="text-xs text-gray-500">Research/development indicator — not a diagnosis.</p>
        </div>
      )}
    </main>
  );
}
