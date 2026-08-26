import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  storeSession(deviceSessionId: string, accessToken: string, accessExpiresAt: string, renewalToken: string, renewalExpiresAt: string): Promise<boolean>;
  clearSession(deviceSessionId: string): Promise<boolean>;
  hasSession(deviceSessionId: string): Promise<boolean>;
  performAuthenticatedRequest(deviceSessionId: string, request: string): Promise<string>;
}

export default TurboModuleRegistry.get<Spec>('HermesSessionVault');
