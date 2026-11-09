"use client";
import { api } from "../lib/api";
import type { Settings, Oracle, Action } from "../lib/types";
export function SettingsView({
  settings,
  oracles,
  busy,
  action,
  setNotice,
}: {
  settings: Settings;
  oracles: Oracle[];
  busy: boolean;
  action: Action;
  setNotice: (message: string) => void;
}) {
  return (
    <>
      <section className="panel">
        <h2>Runtime capabilities</h2>
        <dl>
          <dt>Mode</dt>
          <dd>{settings.mode}</dd>
          <dt>Planner</dt>
          <dd>{settings.planner} · no live provider</dd>
          <dt>Persistence</dt>
          <dd>{settings.storage}</dd>
          <dt>Retention</dt>
          <dd>Artifacts: 24 hours · run metadata: 7 days</dd>
        </dl>
        <h3>Current limitations</h3>
        <ul>
          {settings.limitations.map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
        <details>
          <summary>Last runner isolation probe</summary>
          <pre>{JSON.stringify(settings.isolation_proof, null, 2)}</pre>
        </details>
      </section>
      <section className="panel">
        <h2>Independent requirement review</h2>
        <p>
          Read the requirement and source before attesting. This seals the
          oracle for future runs; it does not accept a finding.
        </p>
        {oracles.map((o) => (
          <article className="oracle" key={o.ref}>
            <h3>{o.ref}</h3>
            <p>{String(o.specification.requirement)}</p>
            <small>Source: fixtures/requirements/oracles.json</small>
            <code>{o.source_sha256}</code>
            <button
              className="secondary"
              disabled={busy || !!o.reviewed_at}
              onClick={() =>
                void action(async () => {
                  await api(
                    "/oracles/" + encodeURIComponent(o.ref) + "/review",
                    { inspected_source_sha256: o.source_sha256 },
                  );
                  setNotice(
                    "Oracle review sealed. Rerun the fixture to create new verified evidence.",
                  );
                })
              }
            >
              {o.reviewed_at
                ? "Review sealed"
                : "I reviewed this requirement and source"}
            </button>
          </article>
        ))}
      </section>
    </>
  );
}
