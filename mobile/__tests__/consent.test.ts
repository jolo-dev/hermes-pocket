import { createConsentReceipt, isConsentValid } from '../src/domain/consent';
import type { components } from '../src/generated/api';

const part: components['schemas']['SharedContextPart'] = {
  part_id: 'part-1',
  kind: 'text',
  media_type: 'text/plain',
  size_bytes: 12,
  digest: `sha256:${'a'.repeat(64)}`,
  text: 'Safe notice',
};

test('consent is bound to content, purpose, destination, and expiry', () => {
  const issuedAt = new Date('2031-01-01T00:00:00Z');
  const expiresAt = new Date('2031-01-01T00:05:00Z');
  const receipt = createConsentReceipt({ receiptId: 'receipt-1', parts: [part], purpose: 'explain', destinationSessionId: 'device-1', issuedAt, expiresAt });
  expect(isConsentValid(receipt, [part], 'explain', 'device-1', new Date('2031-01-01T00:01:00Z'))).toBe(true);
  expect(isConsentValid(receipt, [{ ...part, text: 'Changed notice' }], 'explain', 'device-1', new Date('2031-01-01T00:01:00Z'))).toBe(false);
  expect(isConsentValid(receipt, [part], 'translate', 'device-1', new Date('2031-01-01T00:01:00Z'))).toBe(false);
  expect(isConsentValid(receipt, [part], 'explain', 'device-1', expiresAt)).toBe(false);
});
