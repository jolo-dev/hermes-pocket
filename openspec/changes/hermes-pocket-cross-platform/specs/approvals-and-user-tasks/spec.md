## Purpose

Give users one review surface for agent questions, drafts, approvals, reminders, and task outcomes while preserving explicit control over every consequential action.

## ADDED Requirements

### Requirement: Unified action inbox
The system SHALL present pending approvals, agent questions, drafts, scheduled tasks, and completed outcomes in a single inbox with status, origin, requested capability, and risk information.

#### Scenario: Approval arrives while app is closed
- **WHEN** a paired backend creates an approval request and push delivery succeeds
- **THEN** the user receives a minimal notification that opens the corresponding inbox item after local authentication policy is satisfied

### Requirement: Privacy-minimized push delivery
Push payloads SHALL contain only an opaque event identifier and non-sensitive display category; the app SHALL fetch full content from the authenticated facade after the user opens the event.

#### Scenario: Sensitive approval is pushed
- **WHEN** an approval concerns a private document
- **THEN** APNs or FCM receives no document text, extracted value, personal name, or agent credential

### Requirement: Explicit scoped decisions
Each actionable item SHALL support an explicit allow or deny decision, SHALL show the exact proposed effect and data disclosure, and SHALL permit narrowing scope when the backend declares a narrower option.

#### Scenario: User denies an action
- **WHEN** the user selects deny on a pending approval
- **THEN** the backend records the denial, performs no proposed effect, and returns a terminal or revised status

#### Scenario: User grants narrower scope
- **WHEN** an approval offers one-time and persistent scopes and the user selects one-time
- **THEN** authorization applies only to the identified action instance

### Requirement: User-approved reminders and tasks
The system SHALL treat reminders and personal tasks as drafts until the user reviews their title, date/time, notification behavior, and destination and explicitly creates them.

#### Scenario: Reminder draft is edited before approval
- **WHEN** the user changes the date of an agent-proposed reminder and confirms creation
- **THEN** only the reviewed date is written to the selected local reminder or calendar destination

### Requirement: Idempotent approval resolution
The system SHALL make approval resolution idempotent and SHALL clearly display stale, expired, revoked, or already-resolved outcomes without repeating an effect.

#### Scenario: Approval response is submitted twice
- **WHEN** the same allow decision is received more than once for one approval identifier
- **THEN** the backend returns the existing outcome and executes the approved effect at most once
