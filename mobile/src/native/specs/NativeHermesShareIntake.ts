import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export type NativeSharePart = {
  partId: string;
  kind: string;
  mediaType: string;
  sizeBytes: number;
  digest: string;
  text?: string;
  stagedFileId?: string;
};

export interface Spec extends TurboModule {
  listPending(): Promise<NativeSharePart[]>;
  discard(intakeId: string): Promise<boolean>;
}

export default TurboModuleRegistry.get<Spec>('HermesShareIntake');
