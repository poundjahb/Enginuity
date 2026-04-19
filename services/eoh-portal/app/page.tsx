"use client";

import { useState } from "react";

type SubmitResult = {
  request_id?: string;
  status?: string;
  error?: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function HomePage() {
  const [userIdentity, setUserIdentity] = useState("owner@org.local");
  const [businessContext, setBusinessContext] = useState("Internal automation");
  const [rawText, setRawText] = useState("");
  const [priorityHint, setPriorityHint] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SubmitResult | null>(null);

  const submitRequest = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/requests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel: "web",
          user_identity: userIdentity,
          business_context: businessContext,
          raw_text: rawText,
          priority_hint: priorityHint,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setResult({ error: data?.detail?.message || data?.detail || "Request failed" });
      } else {
        setResult({ request_id: data.request_id, status: data.status });
      }
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : "Network error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 780, margin: "2rem auto", padding: "1.5rem" }}>
      <h1 style={{ margin: 0 }}>Engineering Operations Hub</h1>
      <p style={{ color: "#4b5563" }}>Day 1 - Request Intake</p>

      <form onSubmit={submitRequest} style={{ display: "grid", gap: "0.75rem", background: "white", padding: "1rem", borderRadius: 10, border: "1px solid #d1d5db" }}>
        <label>
          User Identity
          <input value={userIdentity} onChange={(e) => setUserIdentity(e.target.value)} required style={{ width: "100%" }} />
        </label>

        <label>
          Business Context
          <input value={businessContext} onChange={(e) => setBusinessContext(e.target.value)} style={{ width: "100%" }} />
        </label>

        <label>
          Priority
          <select value={priorityHint} onChange={(e) => setPriorityHint(e.target.value)} style={{ width: "100%" }}>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
          </select>
        </label>

        <label>
          Unstructured Request
          <textarea value={rawText} onChange={(e) => setRawText(e.target.value)} required rows={6} style={{ width: "100%" }} />
        </label>

        <button disabled={loading} type="submit" style={{ padding: "0.7rem", borderRadius: 8, border: "none", background: "#0f766e", color: "white", cursor: "pointer" }}>
          {loading ? "Submitting..." : "Submit Request"}
        </button>
      </form>

      {result && (
        <section style={{ marginTop: "1rem", background: "white", padding: "1rem", borderRadius: 10, border: "1px solid #d1d5db" }}>
          {result.error ? (
            <p style={{ color: "#b91c1c", margin: 0 }}>Error: {result.error}</p>
          ) : (
            <>
              <p style={{ margin: "0 0 0.25rem" }}><strong>request_id:</strong> {result.request_id}</p>
              <p style={{ margin: 0 }}><strong>status:</strong> {result.status}</p>
            </>
          )}
        </section>
      )}
    </main>
  );
}
