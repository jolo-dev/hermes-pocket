## Purpose

Provide narrow native integrations where mobile operating systems require them while preventing credential access, application surveillance, and unconfirmed cross-app transitions.

## ADDED Requirements

### Requirement: Native share intake
Android and iOS SHALL provide platform share entry points that pass only the user-selected item into Hermes Pocket for local review and SHALL NOT read unrelated content from the source application.

#### Scenario: iOS share extension receives an image
- **WHEN** the user invokes the Hermes Pocket Share Extension for one image
- **THEN** only that selected image and platform-provided metadata are staged for review in Hermes Pocket

### Requirement: Credential-provider handoff only
On detected or user-identified sign-in contexts, the system SHALL explain that credentials are not available to Hermes Pocket and SHALL offer only a user-initiated handoff to Android Credential Manager or iOS AuthenticationServices/Password AutoFill.

#### Scenario: User requests saved-password help
- **WHEN** the user taps the credential-provider action
- **THEN** the operating system or configured provider owns credential selection and authentication and returns no password, OTP, or recovery secret to Hermes Pocket

### Requirement: Confirmation-gated external navigation
The system SHALL display the exact destination application, integration, or URL before opening it and SHALL launch it only after a local explicit confirmation.

#### Scenario: Agent proposes parcel-tracking app
- **WHEN** the agent proposes opening a configured parcel-tracking destination
- **THEN** the app asks the user to confirm the named destination before issuing the platform navigation request

### Requirement: Privacy-preserving app capability discovery
Android SHALL limit installed-app checks to user-selected or curated capabilities and transmit only task-relevant capability booleans; iOS SHALL use configured integrations or known deep links and SHALL NOT enumerate installed applications.

#### Scenario: Tracking capability is shared
- **WHEN** an Android user has enabled local parcel-tracking guidance and a matching app is available
- **THEN** the server receives a boolean capability and not the package name or installed-app inventory

### Requirement: Honest iOS context boundary
The iOS experience SHALL use share sheet content, screenshot/file import, optional browser extension content, or explicit in-app integrations and SHALL NOT claim or attempt arbitrary cross-app screen inspection or a system-wide overlay.

#### Scenario: iOS user asks for current-screen help
- **WHEN** no content has been explicitly shared to Hermes Pocket
- **THEN** the app instructs the user to share or import the relevant content rather than claiming to inspect another app
