## Purpose

Provide a consistent, multilingual conversation and explicit-sharing experience on iOS and Android without granting background access to unrelated device content.

## ADDED Requirements

### Requirement: Multilingual conversation preferences
The system SHALL let the user configure the mobile interface language and preferred agent reply language independently, and SHALL preserve those preferences per paired device.

#### Scenario: Reply language differs from interface language
- **WHEN** the interface language is German and the preferred reply language is Vietnamese
- **THEN** navigation and controls are rendered in German while new agent replies are requested and identified as Vietnamese

### Requirement: Multimodal conversation
The system SHALL support user-authored text, voice notes, images, and files in a conversation and SHALL render incremental agent response events without representing an incomplete response as final.

#### Scenario: Streamed response completes
- **WHEN** the backend emits response fragments followed by a completion event
- **THEN** the app displays the fragments in order and marks the message complete only after the completion event

#### Scenario: Voice note requires deliberate recording
- **WHEN** a user starts and stops a voice recording
- **THEN** the app presents the resulting voice note for review before it can be sent

### Requirement: Explicit cross-platform sharing
The system SHALL accept user-initiated shares of text, selections, URLs, images, screenshots, and PDFs from platform share surfaces and SHALL require the user to select a destination conversation and confirm the payload before upload.

#### Scenario: Shared URL is reviewed
- **WHEN** the user shares a URL from another application
- **THEN** Hermes Pocket shows the URL and selected conversation and sends it only after confirmation

#### Scenario: Share is cancelled
- **WHEN** the user cancels the share review
- **THEN** the payload is not uploaded or added to a conversation

### Requirement: Failed-send safety
The system SHALL keep unsent user content locally when connectivity fails, disclose that it was not delivered, and SHALL NOT silently retry an attachment upload after its per-item consent has expired or been withdrawn.

#### Scenario: Network fails during consented upload
- **WHEN** an approved attachment upload fails because the service is unavailable
- **THEN** the app marks the message unsent and asks for renewed confirmation before a later upload attempt
