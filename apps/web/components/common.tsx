export function Stamp({ state }: { state: string }) {
  return (
    <span
      className={`stamp ${state === "pass" ? "pass" : state === "failed" || state === "test_error" ? "error" : ""}`}
    >
      {state.replaceAll("_", " ")}
    </span>
  );
}
export const date = (stamp: number) => new Date(stamp * 1000).toLocaleString();
