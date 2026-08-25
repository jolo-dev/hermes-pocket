import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const fixtureDirectory = resolve("fixtures/v1");
const fixtureFiles = readdirSync(fixtureDirectory).filter((name) => name.endsWith(".json"));
const fixtureText = fixtureFiles.map((name) => readFileSync(resolve(fixtureDirectory, name), "utf8"));

describe("shared fictional fixtures", () => {
  it("covers every baseline fixture category", () => {
    expect(fixtureFiles.sort()).toEqual([
      "api-models.json",
      "documents.json",
      "multilingual-chat.json",
      "phishing.json",
      "prohibited-actions.json",
      "sensitive-screens.json",
    ]);
  });

  it.each(fixtureText)("is explicitly fictional and valid JSON", (content) => {
    const fixture = JSON.parse(content) as { fictional?: boolean };
    expect(fixture.fictional).toBe(true);
  });

  it.each(fixtureText)("contains no likely real personal or prohibited data", (content) => {
    expect(content).not.toMatch(/\b(?:\d[ -]*?){13,19}\b/);
    expect(content).not.toMatch(/\b\d{3}-\d{2}-\d{4}\b/);
    expect(content).not.toMatch(/\b(?:password|otp|code)\s*[:=]\s*[A-Za-z0-9]{4,}\b/i);
    expect(content).not.toMatch(/[A-Z0-9._%+-]+@(?!example\.(?:invalid|test)\b)[A-Z0-9.-]+\.[A-Z]{2,}/i);
    expect(content).not.toMatch(/https?:\/\/(?![^/]*\.example\.invalid\b)/i);
  });

  it("uses placeholders rather than sample secrets", () => {
    const sensitiveScreens = fixtureText.find((content) => content.includes("sensitive-screens-001"));
    expect(sensitiveScreens).toContain("[PASSWORD_VALUE]");
    expect(sensitiveScreens).toContain("[OTP_VALUE]");
  });
});
