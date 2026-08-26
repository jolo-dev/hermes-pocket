import NativeHermesSessionVault from '../native/specs/NativeHermesSessionVault';

export type SessionSecretInput = {
  deviceSessionId: string;
  accessToken: string;
  accessExpiresAt: string;
  renewalToken: string;
  renewalExpiresAt: string;
};

export interface SessionVault {
  store(input: SessionSecretInput): Promise<void>;
  clear(deviceSessionId: string): Promise<void>;
  hasSession(deviceSessionId: string): Promise<boolean>;
}

export const sessionVault: SessionVault = {
  async store(input) {
    if (!NativeHermesSessionVault) throw new Error('Secure session storage is unavailable');
    await NativeHermesSessionVault.storeSession(
      input.deviceSessionId,
      input.accessToken,
      input.accessExpiresAt,
      input.renewalToken,
      input.renewalExpiresAt,
    );
  },
  async clear(deviceSessionId) {
    if (!NativeHermesSessionVault) return;
    await NativeHermesSessionVault.clearSession(deviceSessionId);
  },
  async hasSession(deviceSessionId) {
    return NativeHermesSessionVault?.hasSession(deviceSessionId) ?? false;
  },
};
