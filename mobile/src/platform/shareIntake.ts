import type { Spec as NativeShareIntakeSpec } from '../native/specs/NativeHermesShareIntake';
import NativeHermesShareIntake from '../native/specs/NativeHermesShareIntake';
import { assertExactKeys, requireString } from './strictBoundary';

export type StagedSharePart = {
  partId: string;
  kind: 'text' | 'url' | 'image' | 'screenshot' | 'pdf';
  mediaType: string;
  sizeBytes: number;
  digest: string;
  text?: string;
  stagedFileId?: string;
};

const kinds = ['text', 'url', 'image', 'screenshot', 'pdf'] as const;

export function parseStagedSharePart(value: unknown): StagedSharePart {
  assertExactKeys(value, ['partId', 'kind', 'mediaType', 'sizeBytes', 'digest', 'text', 'stagedFileId'], 'share part');
  const kind = requireString(value.kind, 'share kind');
  if (!kinds.includes(kind as StagedSharePart['kind']) || typeof value.sizeBytes !== 'number') {
    throw new Error('Invalid share part');
  }
  const part: StagedSharePart = {
    partId: requireString(value.partId, 'share part id'),
    kind: kind as StagedSharePart['kind'],
    mediaType: requireString(value.mediaType, 'share media type'),
    sizeBytes: value.sizeBytes,
    digest: requireString(value.digest, 'share digest'),
  };
  if (value.text !== undefined) part.text = requireString(value.text, 'share text');
  if (value.stagedFileId !== undefined) part.stagedFileId = requireString(value.stagedFileId, 'staged file id');
  return part;
}

export interface ShareIntakePlatform {
  listPending(): Promise<StagedSharePart[]>;
  discard(intakeId: string): Promise<void>;
}

export function createShareIntakePlatform(native: NativeShareIntakeSpec | null | undefined = NativeHermesShareIntake): ShareIntakePlatform {
  return {
    async listPending() {
      if (!native) return [];
      return (await native.listPending()).map(parseStagedSharePart);
    },
    async discard(intakeId) {
      await native?.discard(intakeId);
    },
  };
}
