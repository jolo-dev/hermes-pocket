import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export type NativeOcrBlock = { blockId: string; text: string; confidence: number };
export type NativeDocumentPage = { pageId: string; stagedFileId: string; textBlocks: NativeOcrBlock[] };

export interface Spec extends TurboModule {
  importDocument(): Promise<NativeDocumentPage[]>;
  discard(captureId: string): Promise<boolean>;
}

export default TurboModuleRegistry.get<Spec>('HermesDocumentCapture');
