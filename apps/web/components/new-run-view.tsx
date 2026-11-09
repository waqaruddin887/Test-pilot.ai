"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../lib/api";
import type { Project, Settings, Action } from "../lib/types";
export function NewRunView({
  projects,
  settings,
  busy,
  action,
}: {
  projects: Project[];
  settings: Settings | null;
  busy: boolean;
  action: Action;
}) {
  const router = useRouter();
  const [project, setProject] = useState(""),
    [path, setPath] = useState("/form"),
    [objective, setObjective] = useState(
      "Check the independent fixture requirement",
    );
  return (
    <form
      className="panel form"
      onSubmit={(e) => {
        e.preventDefault();
        void action(async () => {
          const created = await api<{ run_id: string }>("/runs", {
            project_id: project || projects[0]?.id,
            target_path: path,
            objective,
            max_cases: 1,
            mode: "smoke",
          });
          router.push("/runs/" + created.run_id);
        });
      }}
    >
      <h2>Scope & objective</h2>
      <label>
        Approved project
        <select
          value={project || projects[0]?.id || ""}
          onChange={(e) => setProject(e.target.value)}
          required
        >
          {!projects.length && <option value="">Create a project first</option>}
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} · {p.fixture}
            </option>
          ))}
        </select>
      </label>
      <label>
        Scenario path
        <select value={path} onChange={(e) => setPath(e.target.value)}>
          {[
            ["/form", "Required field"],
            ["/email", "Malformed email"],
            ["/login", "Invalid login rejection"],
            ["/navigation", "Navigation"],
            ["/cart", "Cart arithmetic"],
          ].map(([v, l]) => (
            <option key={v} value={v}>
              {v} — {l}
            </option>
          ))}
        </select>
      </label>
      <label>
        Testing objective
        <textarea
          value={objective}
          onChange={(e) => setObjective(e.target.value)}
          maxLength={1000}
          required
        />
      </label>
      <div className="inset">
        <b>Explicit deterministic smoke run</b>
        <p>
          One case, at most twelve steps. Independently authored requirements
          supply assertions. No provider API is called. A violation triggers one
          clean-context reproduction.
        </p>
      </div>
      <button disabled={busy || !projects.length || !settings?.worker_ready}>
        {busy ? "Submitting…" : "Start fixture run"}
      </button>
      {!settings?.worker_ready && (
        <p className="muted">
          Start the isolated foreground worker before submitting a run.
        </p>
      )}
    </form>
  );
}
