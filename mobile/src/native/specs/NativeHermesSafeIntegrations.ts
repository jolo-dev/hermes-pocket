import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export type NativeIntegrationStatus = { status: string };
export type NativeReminderDraft = {
  title: string;
  scheduledAt: string;
  notificationsEnabled: boolean;
  destinationId: string;
};

export interface Spec extends TurboModule {
  openCredentialProvider(): Promise<NativeIntegrationStatus>;
  openConfirmedDestination(destinationId: string): Promise<NativeIntegrationStatus>;
  createLocalReminder(reminder: NativeReminderDraft): Promise<NativeIntegrationStatus>;
  curatedCapability(capabilityId: string): Promise<boolean>;
}

export default TurboModuleRegistry.get<Spec>('HermesSafeIntegrations');
