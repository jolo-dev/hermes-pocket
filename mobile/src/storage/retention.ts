import type { TemporaryFileStore } from './types';

export async function deleteExpiredWorkingData(store: TemporaryFileStore, now: Date): Promise<string[]> {
  const expired = (await store.list())
    .filter(record => !record.saved && new Date(record.expiresAt).getTime() <= now.getTime())
    .map(record => record.id);
  if (expired.length > 0) await store.discard(expired);
  return expired;
}
