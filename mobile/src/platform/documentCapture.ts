import type { Spec as NativeDocumentCaptureSpec } from '../native/specs/NativeHermesDocumentCapture';
import NativeHermesDocumentCapture from '../native/specs/NativeHermesDocumentCapture';
import { assertExactKeys, requireString } from './strictBoundary';

export type OcrTextBlock = { blockId: string; text: string; confidence: number };
export type DocumentPage = { pageId: string; stagedFileId: string; textBlocks: OcrTextBlock[] };

export function parseDocumentPage(value: unknown): DocumentPage {
  assertExactKeys(value, ['pageId', 'stagedFileId', 'textBlocks'], 'document page');
  if (!Array.isArray(value.textBlocks)) throw new Error('Invalid document page');
  return {
    pageId: requireString(value.pageId, 'page id'),
    stagedFileId: requireString(value.stagedFileId, 'staged file id'),
    textBlocks: value.textBlocks.map(block => {
      assertExactKeys(block, ['blockId', 'text', 'confidence'], 'OCR block');
      if (typeof block.confidence !== 'number' || block.confidence < 0 || block.confidence > 1) {
        throw new Error('Invalid OCR block');
      }
      return {
        blockId: requireString(block.blockId, 'OCR block id'),
        text: requireString(block.text, 'OCR text'),
        confidence: block.confidence,
      };
    }),
  };
}

export interface DocumentCapturePlatform {
  importDocument(): Promise<DocumentPage[]>;
  discard(captureId: string): Promise<void>;
}

export function createDocumentCapturePlatform(native: NativeDocumentCaptureSpec | null | undefined = NativeHermesDocumentCapture): DocumentCapturePlatform {
  return {
    async importDocument() {
      if (!native) return [];
      return (await native.importDocument()).map(parseDocumentPage);
    },
    async discard(captureId) {
      await native?.discard(captureId);
    },
  };
}
