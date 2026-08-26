import type { components } from '../generated/api';

type ApiSchemas = components['schemas'];

export type SessionRecord = Pick<
  ApiSchemas['DeviceSession'],
  'device_session_id' | 'access_expires_at' | 'renewal_expires_at' | 'backend_name' | 'backend_fingerprint'
>;
export type SharedContext = Omit<ApiSchemas['ContextShareCommand'], 'metadata'>;
export type ConversationEvent = ApiSchemas['EventEnvelope'];
export type Approval = ApiSchemas['Approval'];
export type UserTask = ApiSchemas['Task'];
export type ConsentReceipt = ApiSchemas['ConsentReceipt'];
export type PrivacyRecord = ApiSchemas['PrivacyRecord'];

export type Conversation = {
  conversationId: string;
  title: string;
  status: 'active' | 'archived';
  updatedAt: string;
};

export type MessageState = 'draft' | 'sending' | 'streaming' | 'complete' | 'failed';
