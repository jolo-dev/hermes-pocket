import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { Ajv2020 } from "ajv/dist/2020.js";
import addFormatsImport from "ajv-formats";
import { describe, expect, it } from "vitest";
import { parse } from "yaml";

const schemaPath = resolve("schemas/v1/mobile-api.schema.json");
const schema = JSON.parse(readFileSync(schemaPath, "utf8")) as Record<string, unknown>;
const ajv = new Ajv2020({ allErrors: true, strict: true });
const addFormats = addFormatsImport as unknown as (instance: Ajv2020) => Ajv2020;
addFormats(ajv);
ajv.addSchema(schema);

const metadata = {
  request_id: "request-1",
  device_session_id: "device-1",
  policy_version: "v1",
  interface_locale: "en",
  reply_locale: "de",
};

function validate(definition: string, value: unknown): boolean {
  const validator = ajv.compile({ $ref: `${schema.$id as string}#/$defs/${definition}` });
  return validator(value) as boolean;
}

describe("mobile API v1 strict contracts", () => {
  it("loads the OpenAPI 3.1 document", () => {
    const openapi = parse(readFileSync(resolve("openapi/v1.yaml"), "utf8")) as {
      openapi: string;
      paths: Record<string, unknown>;
    };
    expect(openapi.openapi).toBe("3.1.0");
    expect(Object.keys(openapi.paths)).toEqual(expect.arrayContaining([
      "/pairing/claim",
      "/conversations/{conversation_id}/messages",
      "/conversations/{conversation_id}/context-shares",
      "/events",
      "/approvals/{approval_id}/decision",
      "/tasks",
      "/privacy/records",
    ]));
  });

  it("accepts a bounded message command", () => {
    expect(validate("MessageCommand", {
      metadata,
      conversation_id: "conversation-1",
      client_message_id: "message-1",
      source: "user_text",
      text: "Please explain the next safe step.",
      approved_capabilities: ["explain"],
    })).toBe(true);
  });

  it.each([
    ["MessageCommand", {
      metadata,
      conversation_id: "conversation-1",
      client_message_id: "message-1",
      source: "user_text",
      text: "Safe text",
      approved_capabilities: ["explain"],
      raw_device_context: "undeclared",
    }],
    ["MessageCommand", {
      metadata,
      conversation_id: "conversation-1",
      client_message_id: "message-1",
      source: "user_text",
      text: "x".repeat(16001),
      approved_capabilities: ["explain"],
    }],
    ["ContextShareCommand", {
      metadata,
      conversation_id: "conversation-1",
      source: "screen_help",
      purpose: "explain",
      parts: Array.from({ length: 13 }, (_, index) => ({
        part_id: `part-${index}`,
        kind: "text",
        media_type: "text/plain",
        size_bytes: 4,
        digest: `sha256:${"a".repeat(64)}`,
        text: "safe",
      })),
      consent: {
        receipt_id: "receipt-1",
        content_digest: `sha256:${"b".repeat(64)}`,
        purpose: "explain",
        destination_session_id: "device-1",
        approved_part_ids: ["part-1"],
        issued_at: "2026-08-25T07:00:00Z",
        expires_at: "2026-08-25T07:05:00Z",
      },
    }],
    ["PrivacyDeleteCommand", {
      metadata: { ...metadata, installed_apps: ["com.example.private"] },
      category: "share",
      record_ids: ["share-1"],
      delete_remote: true,
    }],
  ])("rejects undeclared or oversized %s payloads", (definition, value) => {
    expect(validate(definition, value)).toBe(false);
  });

  it("keeps released adapter choices limited to Strands", () => {
    expect(validate("VersionInfo", {
      supported_versions: ["v1"],
      minimum_client_version: "0.1.0",
      enabled_capabilities: ["conversation"],
      available_adapters: ["openclaw"],
    })).toBe(false);
  });
});
