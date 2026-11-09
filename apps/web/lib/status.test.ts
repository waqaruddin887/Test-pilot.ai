import assert from "node:assert/strict";
import test from "node:test";
import { outcomeLabel, terminal } from "./status.ts";
test("uncertainty never appears as pass or confirmation", () => {
  for (const state of ["suspected", "inconclusive", "test_error", "verified"]) {
    assert.doesNotMatch(
      outcomeLabel(state),
      /Requirement passed|Confirmed defect/,
    );
  }
  assert.equal(
    outcomeLabel("verified", true, false),
    "Historically accepted · evidence unavailable",
  );
  assert.equal(terminal("completed"), true);
  assert.equal(terminal("verifying"), false);
});
