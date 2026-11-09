export function outcomeLabel(
  machine: string | null,
  confirmed = false,
  available = true,
): string {
  if (confirmed && available) return "Confirmed defect";
  if (!available && confirmed)
    return "Historically accepted · evidence unavailable";
  if (machine === "verified") return "Verified · awaiting review";
  if (machine === "pass") return "Requirement passed";
  if (machine === "suspected") return "Suspected · review required";
  if (machine === "inconclusive") return "Inconclusive";
  if (machine === "test_error") return "Test error";
  return "No assessment yet";
}
export function terminal(state: string): boolean {
  return ["completed", "failed", "cancelled"].includes(state);
}
