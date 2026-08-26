import { createMobileApiClient } from '../generated/api';

export function createPublicMobileApi(baseUrl: string) {
  const client = createMobileApiClient(baseUrl);
  return {
    getVersion: () => client.GET('/version'),
    inspectPairingCode: (pairingCode: string) =>
      client.POST('/pairing/inspect', { body: { pairing_code: pairingCode } }),
  };
}
