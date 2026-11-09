"use client";
import Link from "next/link";
import { api } from "../lib/api";
import type { Project, Run, Finding, Oracle, Settings } from "../lib/types";
import { ProjectsView } from "./projects-view";
import { NewRunView } from "./new-run-view";
import { HistoryView } from "./history-view";
import { RunView } from "./run-view";
import { FindingView } from "./finding-view";
import { SettingsView } from "./settings-view";
import { useCallback, useEffect, useState } from "react";

type View = "projects" | "new" | "history" | "run" | "finding" | "settings";
export default function Console({ view, id }: { view: View; id?: string }) {
  const [projects, setProjects] = useState<Project[]>([]),
    [runs, setRuns] = useState<Run[]>([]);
  const [run, setRun] = useState<Run | null>(null),
    [finding, setFinding] = useState<Finding | null>(null),
    [findings, setFindings] = useState<Finding[]>([]);
  const [settings, setSettings] = useState<Settings | null>(null),
    [oracles, setOracles] = useState<Oracle[]>([]);
  const [error, setError] = useState(""),
    [loading, setLoading] = useState(true),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState("");
  const [secret, setSecret] = useState("");
  const refresh = useCallback(async () => {
    try {
      const [p, r, s] = await Promise.all([
        api<{ items: Project[] }>("/projects"),
        api<{ items: Run[] }>("/runs"),
        api<Settings>("/settings"),
      ]);
      setProjects(p.items);
      setRuns(r.items);
      setSettings(s);
      if (view === "run" && id) {
        const [detail, fs] = await Promise.all([
          api<Run>("/runs/" + id),
          api<{ items: Finding[] }>("/runs/" + id + "/findings"),
        ]);
        setRun(detail);
        setFindings(fs.items);
      }
      if (view === "finding" && id)
        setFinding(await api<Finding>("/findings/" + id));
      if (view === "settings")
        setOracles((await api<{ items: Oracle[] }>("/oracles")).items);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load data");
    } finally {
      setLoading(false);
    }
  }, [view, id]);
  useEffect(() => {
    const initial = setTimeout(() => void refresh(), 0);
    const interval = setInterval(() => void refresh(), 3000);
    return () => {
      clearTimeout(initial);
      clearInterval(interval);
    };
  }, [refresh]);
  async function action(work: () => Promise<void>) {
    setBusy(true);
    setNotice("");
    try {
      await work();
      setError("");
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }
  const titles: Record<View, string> = {
    projects: "Projects",
    new: "New test run",
    history: "Test history",
    run: "Run workspace",
    finding: "Finding detail",
    settings: "Configuration",
  };
  return (
    <div className="shell">
      <a href="#content" className="skip">
        Skip to content
      </a>
      <aside>
        <Link href="/" className="brand">
          <span className="mark">T/</span> TestPilot <small>AI</small>
        </Link>
        <p className="eyebrow">FIXTURE LABORATORY</p>
        <nav aria-label="Main navigation">
          {[
            ["projects", "/", "Projects"],
            ["new", "/runs/new", "New test run"],
            ["history", "/runs", "Test history"],
            ["settings", "/settings", "Configuration"],
          ].map(([key, href, label]) => (
            <Link
              key={key}
              href={href}
              aria-current={view === key ? "page" : undefined}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="scope">
          <span className="dot" /> Controlled environment
          <p>Repository-owned synthetic fixtures only.</p>
          <small>Deterministic planner · no live LLM</small>
        </div>
      </aside>
      <div className="workspace">
        <header>
          <span>
            LOCAL WORKSPACE <span className="divider">/</span> {titles[view]}
          </span>
          <span className="worker">
            {settings?.worker_ready ? "Worker available" : "Worker unavailable"}
          </span>
        </header>
        <main id="content">
          <div className="page-head">
            <div>
              <p className="eyebrow">TESTPILOT AI / {view.toUpperCase()}</p>
              <h1>{titles[view]}</h1>
              <p className="lede">
                {view === "projects"
                  ? "Define the scope. Test the interface. Inspect the evidence."
                  : view === "new"
                    ? "Run a finite, requirement-backed check against an approved synthetic fixture."
                    : "Execution evidence and uncertainty, kept in view."}
              </p>
            </div>
            {view === "projects" && (
              <Link className="primary" href="/runs/new">
                New test run <span aria-hidden>↗</span>
              </Link>
            )}
          </div>
          <div className="mode-note">
            <b>Restricted fixture mode</b>
            <span>
              All pages are served from reviewed repository files inside a
              network-disabled browser. External testing is unavailable.
            </span>
          </div>
          {error && (
            <div className="alert" role="alert">
              {error}
            </div>
          )}
          {notice && (
            <p role="status" className="notice">
              {notice}
            </p>
          )}
          {error.startsWith("401") && (
            <form
              className="panel form"
              onSubmit={(e) => {
                e.preventDefault();
                void action(async () => {
                  await api("/session/bootstrap", { secret });
                  setSecret("");
                });
              }}
            >
              <h2>Unlock local workspace</h2>
              <p>
                Enter the operator secret configured in your local environment.
              </p>
              <label>
                Operator secret
                <input
                  type="password"
                  autoComplete="off"
                  value={secret}
                  onChange={(e) => setSecret(e.target.value)}
                  minLength={32}
                  required
                />
              </label>
              <button disabled={busy}>Unlock</button>
            </form>
          )}
          {loading && <p role="status">Loading workspace…</p>}
          {!loading && !error.startsWith("401") && (
            <>
              {view === "projects" && (
                <ProjectsView
                  projects={projects}
                  runs={runs}
                  busy={busy}
                  action={action}
                  setNotice={setNotice}
                />
              )}
              {view === "new" && (
                <NewRunView
                  projects={projects}
                  settings={settings}
                  busy={busy}
                  action={action}
                />
              )}
              {view === "history" && <HistoryView runs={runs} />}
              {view === "run" && run && id && (
                <RunView
                  run={run}
                  id={id}
                  findings={findings}
                  busy={busy}
                  action={action}
                  setNotice={setNotice}
                />
              )}
              {view === "finding" && finding && id && (
                <FindingView
                  finding={finding}
                  id={id}
                  busy={busy}
                  action={action}
                  setNotice={setNotice}
                />
              )}
              {view === "settings" && settings && (
                <SettingsView
                  settings={settings}
                  oracles={oracles}
                  busy={busy}
                  action={action}
                  setNotice={setNotice}
                />
              )}
            </>
          )}
          <footer>
            TESTPILOT AI{" "}
            <span>Local prototype · synthetic-only · evidence expires</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
