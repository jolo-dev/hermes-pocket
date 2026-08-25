import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const threatModel = readFileSync(resolve("../docs/threat-model.md"), "utf8");

describe("safety documentation traceability", () => {
  it.each([
    "SDP-1",
    "SDP-2",
    "SDP-3",
    "SDP-4",
    "SDP-5",
    "SDP-6",
    "ASH-1",
    "ASH-2",
    "ASH-3",
    "ASH-4",
    "ASH-5",
    "ASH-6",
  ])("documents invariant %s", (invariant) => {
    expect(threatModel).toContain(`| ${invariant} |`);
  });

  it.each([
    "Trust Boundaries",
    "Data Classification and Retention",
    "Prohibited Actions",
    "Platform Capability Boundaries",
    "Android Screen Help Safety Case",
    "Red-Team Cases",
  ])("contains required section %s", (section) => {
    expect(threatModel).toContain(`## ${section}`);
  });
});
