import type { Spec as NativeSafeIntegrationsSpec } from '../native/specs/NativeHermesSafeIntegrations';
import NativeHermesSafeIntegrations from '../native/specs/NativeHermesSafeIntegrations';
import { assertExactKeys, requireString } from './strictBoundary';

export type IntegrationStatus = { status: 'completed' | 'cancelled' | 'unavailable' };
export type ReviewedReminder = {
  title: string;
  scheduledAt: string;
  notificationsEnabled: boolean;
  destinationId: string;
};

export function parseIntegrationStatus(value: unknown): IntegrationStatus {
  assertExactKeys(value, ['status'], 'integration status');
  const status = requireString(value.status, 'integration status');
  if (!['completed', 'cancelled', 'unavailable'].includes(status)) {
    throw new Error('Invalid integration status');
  }
  return { status: status as IntegrationStatus['status'] };
}

export interface SafeIntegrationsPlatform {
  openCredentialProvider(): Promise<IntegrationStatus>;
  openConfirmedDestination(destinationId: string): Promise<IntegrationStatus>;
  createLocalReminder(reminder: ReviewedReminder): Promise<IntegrationStatus>;
  curatedCapability(capabilityId: string): Promise<boolean>;
}

export function createSafeIntegrationsPlatform(native: NativeSafeIntegrationsSpec | null | undefined = NativeHermesSafeIntegrations): SafeIntegrationsPlatform {
  return {
    async openCredentialProvider() {
      return native ? parseIntegrationStatus(await native.openCredentialProvider()) : { status: 'unavailable' };
    },
    async openConfirmedDestination(destinationId) {
      return native ? parseIntegrationStatus(await native.openConfirmedDestination(destinationId)) : { status: 'unavailable' };
    },
    async createLocalReminder(reminder) {
      return native ? parseIntegrationStatus(await native.createLocalReminder(reminder)) : { status: 'unavailable' };
    },
    async curatedCapability(capabilityId) {
      return native ? native.curatedCapability(capabilityId) : false;
    },
  };
}
