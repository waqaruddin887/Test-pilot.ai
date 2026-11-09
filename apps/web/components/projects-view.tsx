"use client";
import Link from "next/link";
import { useState } from "react";
import { Stamp } from "./common";
import { api } from "../lib/api";
import type { Project, Run, Action } from "../lib/types";
export function ProjectsView({
  projects,
  runs,
  busy,
  action,
  setNotice,
}: {
  projects: Project[];
  runs: Run[];
  busy: boolean;
  action: Action;
  setNotice: (message: string) => void;
}) {
  const [name, setName] = useState("Synthetic demo"),
    [fixture, setFixture] = useState("synthetic-control-v1");
  return (
    <>
      <div className="metrics">
        <div>
          <small>APPROVED PROJECTS</small>
          <strong>{projects.length}</strong>
        </div>
        <div>
          <small>RECORDED RUNS</small>
          <strong>{runs.length}</strong>
        </div>
        <div>
          <small>PLANNING MODE</small>
          <strong className="word">Deterministic</strong>
        </div>
      </div>
      <div className="section-title">
        <h2>Approved projects</h2>
        <span>Exact fixture scope · seven-day authorization</span>
      </div>
      {!projects.length && (
        <div className="empty">
          <h3>Your first controlled test starts here</h3>
          <p>
            Create a project using a supplied synthetic fixture. No domain
            registration or third-party authorization is implied.
          </p>
        </div>
      )}
      <div className="cards">
        {projects.map((p) => (
          <article className="panel" key={p.id}>
            <div className="card-top">
              <span className="eyebrow">SYNTHETIC / V1</span>
              <Stamp state="authorized fixture" />
            </div>
            <h2>{p.name}</h2>
            <p>
              {p.fixture === "synthetic-control-v1"
                ? "Known-good reference fixture"
                : "Seeded demonstration fixture"}
            </p>
            <code>http://fixture.test</code>
            <div className="card-bottom">
              <span>5 requirement scenarios</span>
              <Link href="/runs/new">Create run →</Link>
            </div>
          </article>
        ))}
      </div>
      <form
        className="panel form"
        onSubmit={(e) => {
          e.preventDefault();
          void action(async () => {
            await api("/projects", {
              name,
              fixture_authorization_ref: fixture,
            });
            setNotice(
              "Project created with expiring synthetic-only authorization.",
            );
          });
        }}
      >
        <h2>Create approved project</h2>
        <label>
          Project name
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={120}
            required
          />
        </label>
        <label>
          Repository fixture
          <select value={fixture} onChange={(e) => setFixture(e.target.value)}>
            <option value="synthetic-control-v1">Known-good control</option>
            <option value="synthetic-seeded-v1">Seeded defects</option>
          </select>
        </label>
        <button disabled={busy}>Create project</button>
      </form>
    </>
  );
}
