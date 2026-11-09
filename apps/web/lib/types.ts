import type { components } from "../../../packages/contracts/api";
export type Schemas = components["schemas"];
export type Project = Schemas["ProjectResponse"];
export type Run = Schemas["RunResponse"];
export type Finding = Schemas["FindingResponse"];
export type Oracle = {
  ref: string;
  specification: Record<string, unknown>;
  source_sha256: string;
  reviewed_at: number | null;
};
export type Settings = {
  worker_ready: boolean;
  mode: string;
  planner: string;
  storage: string;
  limitations: string[];
  isolation_proof: unknown;
};

export type Action = (work: () => Promise<void>) => Promise<void>;
