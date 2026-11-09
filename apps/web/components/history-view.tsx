"use client";
import Link from "next/link";
import { Stamp, date } from "./common";
import type { Run } from "../lib/types";
export function HistoryView({ runs }: { runs: Run[] }) {
  return (
    <section className="panel">
      <h2>Recorded executions</h2>
      {!runs.length ? (
        <div className="empty">
          No runs yet. <Link href="/runs/new">Create a fixture run</Link>.
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Objective / path</th>
                <th>Workflow state</th>
                <th>Created</th>
                <th>Run</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.id}>
                  <td>
                    {r.objective}
                    <small>
                      {r.target_path} · {r.mode}
                    </small>
                  </td>
                  <td>
                    <Stamp state={r.state} />
                  </td>
                  <td>{date(r.created_at)}</td>
                  <td>
                    <Link href={"/runs/" + r.id}>Inspect →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
