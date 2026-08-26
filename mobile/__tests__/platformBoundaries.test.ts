import { parseDocumentPage } from '../src/platform/documentCapture';
import { parseIntegrationStatus } from '../src/platform/safeIntegrations';
import { parseStagedSharePart } from '../src/platform/shareIntake';

test('share intake rejects undeclared source metadata', () => {
  const share = { partId: 'part-1', kind: 'text', mediaType: 'text/plain', sizeBytes: 4, digest: `sha256:${'a'.repeat(64)}`, text: 'safe' };
  expect(parseStagedSharePart(share)).toEqual(share);
  expect(() => parseStagedSharePart({ ...share, sourcePackage: 'unrelated.app' })).toThrow('Invalid share part');
});

test('document capture rejects raw native metadata', () => {
  const page = { pageId: 'page-1', stagedFileId: 'file-1', textBlocks: [{ blockId: 'block-1', text: 'Fictional notice', confidence: 0.9 }] };
  expect(parseDocumentPage(page)).toEqual(page);
  expect(() => parseDocumentPage({ ...page, rawVisionResult: { unsafe: true } })).toThrow('Invalid document page');
});

test('safe integration status cannot carry credential or destination values', () => {
  expect(parseIntegrationStatus({ status: 'cancelled' })).toEqual({ status: 'cancelled' });
  expect(() => parseIntegrationStatus({ status: 'completed', password: 'forbidden' })).toThrow('Invalid integration status');
  expect(() => parseIntegrationStatus({ status: 'completed', packageName: 'installed.app' })).toThrow('Invalid integration status');
});
