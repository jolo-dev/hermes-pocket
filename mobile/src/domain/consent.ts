import { sha256 } from '@noble/hashes/sha2.js';
import { bytesToHex, utf8ToBytes } from '@noble/hashes/utils.js';
import type { components } from '../generated/api';

type SharedPart = components['schemas']['SharedContextPart'];
type ConsentReceipt = components['schemas']['ConsentReceipt'];

function canonicalPart(part: SharedPart): string {
  return JSON.stringify({
    digest: part.digest,
    kind: part.kind,
    media_type: part.media_type,
    part_id: part.part_id,
    size_bytes: part.size_bytes,
    text: part.text ?? null,
    upload_id: part.upload_id ?? null,
  });
}

export function digestSharedParts(parts: SharedPart[]): string {
  const canonical = parts.map(canonicalPart).join('\n');
  return `sha256:${bytesToHex(sha256(utf8ToBytes(canonical)))}`;
}

export function createConsentReceipt(input: {
  receiptId: string;
  parts: SharedPart[];
  purpose: ConsentReceipt['purpose'];
  destinationSessionId: string;
  issuedAt: Date;
  expiresAt: Date;
}): ConsentReceipt {
  return {
    receipt_id: input.receiptId,
    content_digest: digestSharedParts(input.parts),
    purpose: input.purpose,
    destination_session_id: input.destinationSessionId,
    approved_part_ids: input.parts.map(part => part.part_id),
    issued_at: input.issuedAt.toISOString(),
    expires_at: input.expiresAt.toISOString(),
  };
}

export function isConsentValid(
  receipt: ConsentReceipt,
  parts: SharedPart[],
  purpose: ConsentReceipt['purpose'],
  destinationSessionId: string,
  now: Date,
): boolean {
  return (
    receipt.content_digest === digestSharedParts(parts) &&
    receipt.purpose === purpose &&
    receipt.destination_session_id === destinationSessionId &&
    receipt.approved_part_ids.length === parts.length &&
    parts.every(part => receipt.approved_part_ids.includes(part.part_id)) &&
    new Date(receipt.issued_at).getTime() <= now.getTime() &&
    new Date(receipt.expires_at).getTime() > now.getTime()
  );
}
