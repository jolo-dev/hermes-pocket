## Why

People who run a self-hosted agent need a trustworthy mobile surface for conversation, shared context, and approvals without giving the agent unrestricted access to their phone or secrets. Hermes Pocket provides that surface on both iOS and Android while being explicit about platform limits and requiring user approval for consequential actions.

## What Changes

- Add a Flutter-based iOS and Android companion with multilingual text/voice conversations, streamed responses, file sharing, and locally controlled language and privacy preferences.
- Add explicit share and document flows for text, URLs, images, screenshots, and PDFs, including on-device OCR where available, preview/redaction, explanation, translation, and per-item upload consent.
- Add an approvals inbox with push notifications for agent questions, drafts, reminder/task proposals, and completed work; sensitive actions require scoped, explicit user decisions.
- Add QR/device-code pairing, device-bound authenticated sessions, revocation, local data inspection/deletion, and opt-in non-secret memory.
- Add a mobile-facing FastAPI/Strands service on Bedrock AgentCore Runtime behind an authenticated facade, with a compact adapter boundary for later verified Hermes and OpenClaw integrations.
- Add narrow Swift/iOS and Kotlin/Android modules for share extensions, OCR/scanning, notifications, credential-provider handoff, and approved deep links.
- Add Android Screen Help as an opt-in beta with a user-tapped overlay, AccessibilityService sanitization, local preview, redaction, and minimized request data.
- Define iOS context sharing through the share sheet, screenshot import, optional browser extension, and direct integrations; arbitrary cross-app inspection and system-wide overlays are not supported or presented as platform parity.
- Prohibit capture, transmission, storage, or logging of passwords, OTPs, recovery codes, card data, and bank-account data. Credentials remain with Android Credential Manager or iOS AuthenticationServices.
- Prohibit autonomous payments, purchases, contract acceptance, form submission, credential entry, cross-app typing, account changes, and message sending; the product may explain or draft but not execute these action classes.

## Capabilities

### New Capabilities
- `mobile-conversation-and-sharing`: Multilingual chat, voice, attachments, explicit cross-platform sharing, and streamed agent responses.
- `private-document-assistance`: Local document capture/OCR, disclosure preview, consented explanation/translation, and safe local retention.
- `approvals-and-user-tasks`: Push-backed approval inbox and user-approved reminders/tasks with risk-aware decisions and no autonomous consequential actions.
- `device-pairing-and-privacy-controls`: QR pairing, authenticated device sessions, revocation, local privacy controls, deletion, and opt-in memory.
- `agent-backend-adapters`: Mobile facade and adapter contract for the initial Strands backend and later verified Hermes/OpenClaw integrations.
- `platform-safe-integrations`: Narrow native integrations for share, notifications, credential-provider handoff, and confirmation-gated deep links without credential access or app surveillance.
- `android-screen-help`: Android-only, opt-in accessibility/overlay assistance with user activation, sanitization, local preview, and minimized transmission.
- `safety-and-data-policy`: Cross-cutting sensitive-data exclusion, untrusted-content handling, action restrictions, and conservative uncertainty behavior.

### Modified Capabilities

None.

## Impact

- Adds a `mobile/` Flutter application with limited Swift and Kotlin platform modules.
- Adds a Python FastAPI/Strands service, versioned mobile API contracts, policy/redaction components, and Bedrock AgentCore Runtime deployment infrastructure behind an authenticated facade.
- Introduces secure local storage, QR pairing, push notifications through APNs/FCM, local OCR adapters, share extensions/receivers, and platform credential handoff dependencies.
- Requires privacy, threat-model, platform-disclosure, accessibility, localization, backend-contract, and end-to-end safety testing across iOS, Android, and the service.
- Does not claim unverified Hermes/OpenClaw compatibility; those integrations remain adapter implementations contingent on stable, verified remote authentication and API contracts.
