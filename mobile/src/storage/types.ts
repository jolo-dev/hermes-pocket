import type { PrivacyRecord } from '../domain/models';

export interface StructuredStore {
  listPrivacyRecords(): Promise<PrivacyRecord[]>;
  deleteRecords(recordIds: string[]): Promise<void>;
}

export type TemporaryRecord = {
  id: string;
  expiresAt: string;
  saved: boolean;
};

export interface TemporaryFileStore {
  list(): Promise<TemporaryRecord[]>;
  discard(ids: string[]): Promise<void>;
}

// Session secrets deliberately have write/use/clear operations and no read operation.
export interface SecretOperations {
  storeSession(input: {
    deviceSessionId: string;
    accessToken: string;
    accessExpiresAt: string;
    renewalToken: string;
    renewalExpiresAt: string;
  }): Promise<void>;
  clearSession(deviceSessionId: string): Promise<void>;
  performAuthenticatedRequest(deviceSessionId: string, request: string): Promise<string>;
}
