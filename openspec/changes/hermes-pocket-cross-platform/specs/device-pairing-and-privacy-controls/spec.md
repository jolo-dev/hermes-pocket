## Purpose

Bind each phone to a user-controlled agent through revocable credentials and give the user understandable control over local data, sessions, and optional memory.

## ADDED Requirements

### Requirement: One-time device pairing
The system SHALL pair through an owner-generated, single-use, expiring QR or device code and SHALL show the backend identity and requested device permissions before the user claims it.

#### Scenario: Valid code is claimed
- **WHEN** the user confirms an unexpired unused pairing code for the displayed backend
- **THEN** the facade creates a distinct device session and invalidates the code

#### Scenario: Pairing code is reused
- **WHEN** a previously claimed code is submitted again
- **THEN** the facade rejects it without creating another session

### Requirement: Device-bound authenticated sessions
The system SHALL use TLS and short-lived, rotatable access credentials bound to a device session, SHALL protect retained secrets with platform secure storage, and SHALL never place AWS or AgentCore control-plane credentials in the mobile application.

#### Scenario: Access credential expires
- **WHEN** a paired device presents an expired access credential and a valid device-bound renewal credential
- **THEN** the facade rotates the session credential without exposing infrastructure credentials

### Requirement: Pairing revocation
The phone user and deployment owner SHALL each be able to revoke a device, after which new API calls and event delivery for that session SHALL be rejected.

#### Scenario: Lost phone is revoked remotely
- **WHEN** the deployment owner revokes the lost phone's device identifier
- **THEN** subsequent refresh, message, approval, and event requests from that session are denied

### Requirement: Inspectable local privacy controls
The app SHALL disclose what categories of local and remote data it uses, allow deletion of conversations, documents, cached shares, and pairing state, and explain which deletion operations also require an authenticated backend request.

#### Scenario: User deletes local document history
- **WHEN** the user confirms deletion of document history
- **THEN** app-managed source files, derived text, and local metadata for those documents are removed

### Requirement: Opt-in non-secret memory
Agent memory SHALL be disabled by default for mobile-derived context, SHALL require explicit consent for each retained category, SHALL be inspectable and deletable, and SHALL reject sensitive-data categories regardless of consent.

#### Scenario: User approves reminder-summary memory
- **WHEN** the user opts to retain a non-secret reminder summary for a disclosed duration
- **THEN** memory stores only the approved summary fields and retention metadata, not the source document or sensitive financial identifiers
