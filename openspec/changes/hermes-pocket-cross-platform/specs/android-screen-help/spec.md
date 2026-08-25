## Purpose

Offer an Android-only, consent-first beta that explains the current accessible screen from a user-requested, sanitized snapshot rather than continuous monitoring or autonomous control.

## ADDED Requirements

### Requirement: Explicit opt-in and disclosure
Android Screen Help SHALL remain disabled until the user separately completes an explanatory onboarding flow and enables required accessibility and overlay permissions, and SHALL provide a visible way to disable the feature.

#### Scenario: User declines accessibility access
- **WHEN** the user selects "Not now" during Screen Help setup
- **THEN** the main cross-platform app remains usable and no accessibility capture or overlay starts

### Requirement: User-activated snapshot only
The service SHALL inspect only the active window after the user taps the help control, SHALL NOT retain accessibility event history, and SHALL NOT tap, type, scroll, submit, or otherwise operate another application.

#### Scenario: Accessibility event occurs without a help tap
- **WHEN** another app emits an accessibility event while no Screen Help request is active
- **THEN** Hermes Pocket stores and transmits no screen snapshot or event content

### Requirement: Sensitive-context suppression
The service SHALL exclude password-marked nodes and SHALL suppress screen text and screenshots for login, OTP, credential-provider, system permission, Android settings, and other configured sensitive contexts.

#### Scenario: Password field is present
- **WHEN** the active accessibility tree includes a password-marked field and a sign-in label
- **THEN** the preview contains no field value and offers local credential-provider safety guidance instead of a screen-content upload

### Requirement: Local sanitized preview
Before any Screen Help request is sent, the app SHALL show the foreground app label or category, extracted text count, redaction summary, optional screenshot state, and the exact send/cancel choice.

#### Scenario: User cancels preview
- **WHEN** the user reviews a sanitized Screen Help snapshot and selects cancel
- **THEN** the snapshot is discarded from working memory or cache and no request is transmitted

### Requirement: Minimized Screen Help request
An approved request SHALL include only the user question, locale/preferences, coarse foreground-app context, sanitized visible text, explicitly approved capability flags, policy version, and an explicitly approved redacted screenshot when selected.

#### Scenario: Screenshot is not approved
- **WHEN** the user approves sanitized text but does not approve the screenshot
- **THEN** the request contains no screenshot bytes or screenshot reference

### Requirement: Platform-specific labeling
The feature SHALL be labeled "Android Screen Help (beta)" or an equivalent localized label and SHALL NOT be presented as available with the same capability on iOS.

#### Scenario: Capability comparison is displayed
- **WHEN** the user views platform capability information
- **THEN** Android Screen Help is identified as Android-only and the iOS share/screenshot alternatives are stated
