## Purpose

Turn explicitly captured or imported documents into understandable explanations and translations while keeping source material local unless the user approves a specific disclosure.

## ADDED Requirements

### Requirement: Local-first document intake
The system SHALL support camera capture and import of images and PDFs, SHALL perform OCR on device where the platform supports it, and SHALL keep original document content local by default.

#### Scenario: OCR succeeds locally
- **WHEN** the user imports a supported document and on-device OCR is available
- **THEN** the app displays extracted text without uploading the original document

#### Scenario: Cloud assistance is unavailable
- **WHEN** a document has been captured while the device is offline
- **THEN** the document and any local OCR result remain available locally and the app clearly states that cloud explanation is unavailable

### Requirement: Per-document disclosure preview
Before transmitting document text or page images, the system SHALL show the exact selected content, identified redactions, destination agent, and purpose, and SHALL offer a one-time send decision rather than blanket document consent.

#### Scenario: User sends OCR text only
- **WHEN** the preview contains OCR text and source page images and the user selects text-only disclosure
- **THEN** the request contains the approved redacted text and no page image

#### Scenario: User declines disclosure
- **WHEN** the user declines the document consent sheet
- **THEN** neither OCR text nor page images leave the device

### Requirement: Structured document assistance
The system SHALL support explanation, translation, and extraction of relevant entities such as issuer, amount, and deadline, SHALL distinguish extracted facts from suggestions, and SHALL expose uncertainty for values that cannot be verified confidently.

#### Scenario: Deadline has low confidence
- **WHEN** the service cannot confidently distinguish between two possible deadline dates
- **THEN** the result labels the deadline as requiring verification and does not present either date as certain

### Requirement: Local retention control
The system SHALL remove temporary source files from working cache after a result is saved or discarded, and SHALL let the user inspect and delete retained document records and derived text.

#### Scenario: User discards a completed scan
- **WHEN** the user discards a scan after reviewing its result
- **THEN** temporary source pages, OCR working data, and the unsaved result are deleted from app-managed storage

### Requirement: Document actions remain drafts
Document assistance SHALL produce only reviewable proposals for reminders or tasks and SHALL NOT directly pay, submit, sign, accept, or transmit a document to a third party.

#### Scenario: Invoice contains a payment request
- **WHEN** an invoice is explained and includes an amount and due date
- **THEN** the system may propose a reminder but does not initiate payment or submission
