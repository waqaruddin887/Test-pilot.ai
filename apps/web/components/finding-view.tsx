"use client";
import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { outcomeLabel } from "../lib/status";
import { api } from "../lib/api";
import type { Finding, Action } from "../lib/types";
export function FindingView({
  finding,
  id,
  busy,
  action,
  setNotice,
}: {
  finding: Finding;
  id: string;
  busy: boolean;
  action: Action;
  setNotice: (message: string) => void;
}) {
  const [reason, setReason] = useState(""),
    [inspected, setInspected] = useState(false);
  return (
    <>
      <div className="run-heading">
        <div>
          <h2>{finding.oracle_ref}</h2>
          <p>
            {outcomeLabel(
              finding.machine_state,
              finding.confirmed,
              finding.evidence_available,
            )}
          </p>
        </div>
        <Link href={"/runs/" + finding.run_id}>View run & steps →</Link>
      </div>
      <div className="two-col">
        <section className="panel">
          <h2>Independent oracle</h2>
          <p>
            {String(finding.oracle?.requirement || "Requirement unavailable")}
          </p>
          <pre>{JSON.stringify(finding.oracle, null, 2)}</pre>
          <p>
            Reproduced in clean context:{" "}
            <b>{finding.reproduced ? "Yes" : "No"}</b>
          </p>
          <p>
            Human review: <b>{finding.review_state}</b>
          </p>
          <p>{finding.reason.replaceAll("_", " ")}</p>
        </section>
        <section className="panel">
          <h2>Evidence manifest</h2>
          <p>
            {finding.evidence_available
              ? "Both attempts have current integrity-checked evidence."
              : "Evidence is incomplete, expired, or unavailable. Acceptance is blocked."}
          </p>
          {Array.isArray(finding.manifest.artifacts) &&
            finding.manifest.artifacts
              .filter((a): a is string => typeof a === "string")
              .map((a, i) => (
                <div className="artifact" key={a}>
                  <a href={"/api/artifacts/" + a} download>
                    {i % 2 === 0 ? "Screenshot" : "Browser trace"} ·{" "}
                    {i < 2 ? "initial" : "reproduction"} ↓
                  </a>
                  {i % 2 === 0 && finding.evidence_available && (
                    <a
                      href={"/api/artifacts/" + a}
                      target="_blank"
                      rel="noreferrer"
                      aria-label="Open screenshot preview"
                    >
                      <Image
                        unoptimized
                        src={"/api/artifacts/" + a}
                        alt={`${i < 2 ? "Initial" : "Reproduction"} failed assertion screenshot`}
                        width={500}
                        height={360}
                      />
                    </a>
                  )}
                </div>
              ))}
          <details>
            <summary>Manifest & integrity hash</summary>
            <code>{finding.manifest_sha256}</code>
            <pre>{JSON.stringify(finding.manifest, null, 2)}</pre>
          </details>
        </section>
      </div>
      <form className="panel form" onSubmit={(e) => e.preventDefault()}>
        <h2>Human disposition</h2>
        <p>
          Oracle review and finding review are separate. Reviewing a requirement
          in Configuration enables verification on a new run.
        </p>
        <label>
          Review reason
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            maxLength={1000}
            required
          />
        </label>
        <label className="check">
          <input
            type="checkbox"
            checked={inspected}
            onChange={(e) => setInspected(e.target.checked)}
          />
          I inspected both attempts, the independent oracle and current evidence
          manifest.
        </label>
        <div className="actions">
          {(["accepted", "dismissed", "unreviewed"] as const).map(
            (decision) => (
              <button
                key={decision}
                className={decision === "accepted" ? "" : "secondary"}
                disabled={
                  busy ||
                  !reason.trim() ||
                  (decision === "accepted" &&
                    (!inspected ||
                      finding.machine_state !== "verified" ||
                      !finding.evidence_available))
                }
                onClick={() =>
                  void action(async () => {
                    await api("/findings/" + id + "/reviews", {
                      decision,
                      reason,
                      expected_review_sequence: finding.review_sequence,
                      inspected_manifest_sha256: inspected
                        ? finding.manifest_sha256
                        : null,
                    });
                    setNotice(
                      "Review appended. Original evidence is unchanged.",
                    );
                  })
                }
              >
                {decision === "accepted"
                  ? "Accept verified finding"
                  : decision === "dismissed"
                    ? "Dismiss"
                    : "Reopen review"}
              </button>
            ),
          )}
        </div>
      </form>
    </>
  );
}
