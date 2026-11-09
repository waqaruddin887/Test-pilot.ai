"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Stamp, date } from "./common";
import { outcomeLabel, terminal } from "../lib/status";
import { api } from "../lib/api";
import type { Run, Finding, Action } from "../lib/types";
export function RunView({
  run,
  id,
  findings,
  busy,
  action,
  setNotice,
}: {
  run: Run;
  id: string;
  findings: Finding[];
  busy: boolean;
  action: Action;
  setNotice: (message: string) => void;
}) {
  const router = useRouter();
  return (
    <>
      <div className="run-heading">
        <div>
          <h2>{run.objective}</h2>
          <code>{run.target_path}</code>
          <p>{outcomeLabel(run.assessment ?? null)}</p>
        </div>
        <div className="actions">
          <Stamp state={run.state} />
          {!terminal(run.state) && (
            <button
              className="secondary"
              disabled={busy || run.cancel_requested}
              onClick={() =>
                void action(async () => {
                  await api("/runs/" + id + "/cancel", {});
                  setNotice(
                    "Cancellation requested; waiting for process teardown.",
                  );
                })
              }
            >
              {run.cancel_requested ? "Stopping…" : "Cancel run"}
            </button>
          )}
          {terminal(run.state) && (
            <button
              disabled={busy}
              onClick={() =>
                void action(async () => {
                  const next = await api<{ run_id: string }>(
                    "/runs/" + id + "/rerun",
                    {},
                  );
                  router.push("/runs/" + next.run_id);
                })
              }
            >
              Rerun fixture
            </button>
          )}
        </div>
      </div>
      {run.reason && <p className="alert">{run.reason}</p>}
      <section className="panel">
        <h2>Workflow</h2>
        <ol className="timeline">
          {run.events?.map((e, i) => (
            <li key={i}>
              <b>{e.state}</b>
              <small>{date(e.created_at)}</small>
            </li>
          ))}
        </ol>
        <p className="muted">
          “Completed” describes the workflow, not the absence of defects.
        </p>
      </section>
      <section className="panel">
        <h2>Findings & review</h2>
        {!findings.length ? (
          <p>
            {run.assessment === "pass"
              ? "The executed requirement passed. This does not establish the entire application is defect-free."
              : "No finding recorded yet."}
          </p>
        ) : (
          findings.map((f) => (
            <Link className="finding-row" key={f.id} href={"/findings/" + f.id}>
              <div>
                <b>{f.oracle_ref}</b>
                <p>
                  {outcomeLabel(
                    f.machine_state,
                    f.confirmed,
                    f.evidence_available,
                  )}
                </p>
                <small>
                  {f.reason.replaceAll("_", " ")} · reproduced:{" "}
                  {f.reproduced ? "yes" : "no"}
                </small>
              </div>
              <span>Inspect evidence →</span>
            </Link>
          ))
        )}
      </section>
      <section className="panel">
        <h2>Reproduction steps</h2>
        {run.plan ? (
          <>
            {run.plan.cases.map((c) => (
              <div key={c.id}>
                <h3>{c.title}</h3>
                <ol className="steps">
                  {c.steps.map((s) => (
                    <li key={s.id}>
                      <b>{s.action.replaceAll("_", " ")}</b>
                      <code>{JSON.stringify(s)}</code>
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </>
        ) : (
          <p>Plan not available yet.</p>
        )}
      </section>
      {run.attempts?.map((a) => (
        <section className="panel" key={a.id}>
          <h2>
            {a.kind} attempt <Stamp state={a.assessment || "pending"} />
          </h2>
          {a.steps.map((s, i) => (
            <details key={i}>
              <summary>
                {String(s.step_id)} · {String(s.status)}
              </summary>
              <pre>{JSON.stringify(s, null, 2)}</pre>
            </details>
          ))}
        </section>
      ))}
      <details className="panel">
        <summary>Planner & execution provenance</summary>
        <pre>{JSON.stringify(run.provenance, null, 2)}</pre>
      </details>
    </>
  );
}
