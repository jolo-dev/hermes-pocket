import { deleteExpiredWorkingData } from '../src/storage/retention';
import type { TemporaryFileStore, TemporaryRecord } from '../src/storage/types';

test('retention cleanup deletes expired working data but preserves saved records', async () => {
  const records: TemporaryRecord[] = [
    { id: 'expired', expiresAt: '2031-01-01T00:00:00Z', saved: false },
    { id: 'saved', expiresAt: '2031-01-01T00:00:00Z', saved: true },
    { id: 'active', expiresAt: '2031-01-01T01:00:00Z', saved: false },
  ];
  const discarded: string[] = [];
  const store: TemporaryFileStore = {
    async list() { return records; },
    async discard(ids) { discarded.push(...ids); },
  };
  expect(await deleteExpiredWorkingData(store, new Date('2031-01-01T00:30:00Z'))).toEqual(['expired']);
  expect(discarded).toEqual(['expired']);
});
