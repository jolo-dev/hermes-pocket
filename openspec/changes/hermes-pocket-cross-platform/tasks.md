## 1. Repository, Safety Baseline, and Contracts

- [x] 1.1 Update the `mobile/`, `service/`, `contracts/`, `infra/`, and `docs/` project structure for pinned React Native, Node.js, TypeScript, Python, and infrastructure toolchains and verify dependency installation succeeds in clean environments without Flutter tooling.
- [x] 1.2 Document the threat model, trust boundaries, data classification, prohibited data/actions, platform capability differences, and red-team cases and verify the documentation covers every invariant in `safety-and-data-policy` and `android-screen-help`.
- [x] 1.3 Define versioned JSON/OpenAPI contracts for pairing, messages, shared context, SSE events, approvals, tasks, privacy controls, and errors and verify strict schema fixtures reject undeclared fields and oversized payloads.
- [x] 1.4 Add shared fictional fixtures for multilingual chat, German/English documents, phishing content, login/OTP screens, and prohibited action requests and verify no fixture contains real personal data.
- [ ] 1.5 Configure deterministic OpenAPI/JSON Schema generation into `mobile/src/generated/api/`, consume the generated client from TypeScript, and verify regeneration, TypeScript compilation, Python serialization, and shared fixtures produce no drift.

## 2. Deterministic Service Policy

- [x] 2.1 Scaffold the FastAPI service with health, structured error, request-correlation, and privacy-safe logging middleware and verify service unit tests and a container health smoke test pass.
- [x] 2.2 Implement strict request allowlists, bounded content validation, and source classification and verify contract tests reject unbounded screen, accessibility, app-inventory, and document dumps before backend invocation.
- [x] 2.3 Implement deterministic password, OTP, recovery-code, card, and bank-data detection/redaction with conservative rejection and verify focused tests assert sensitive values never reach model mocks, logs, or errors.
- [x] 2.4 Implement untrusted-content prompt construction that separates policy, user intent, approved capabilities, and captured content and verify prompt-injection fixtures cannot add tools, change policy, or authorize an action.
- [x] 2.5 Implement structured response validation, confidence downgrading, and the prohibited-action denylist and verify payment, purchase, contract, claim, form-submit, credential-entry, typing, account-change, and send-message outputs are blocked.

## 3. Facade, Pairing, and Agent Adapter

- [x] 3.1 Define the backend-neutral adapter protocol and conformance test suite for pairing/session behavior, message streaming, approvals, tasks, errors, and revocation and verify a fake adapter passes all required cases.
- [x] 3.2 Implement the Strands adapter with Vietnamese/German/English reply selection, structured outputs, no prohibited tools, and an AgentCore invocation boundary and verify mocked runtime tests preserve event order and correlation IDs.
- [x] 3.3 Implement expiring single-use pairing claims, backend identity display data, device records, short-lived access tokens, renewal rotation, and replay protection and verify claim reuse and expired-code tests fail closed.
- [x] 3.4 Implement authenticated device revocation by phone and owner and verify revoked sessions cannot refresh, send messages, fetch events, resolve approvals, or retain push associations.
- [x] 3.5 Add facade endpoints for version negotiation, conversations, context shares, events, approvals, tasks, privacy inspection/deletion, and memory consent and verify end-to-end API tests exercise authorization and structured compatibility failures.
- [x] 3.6 Add an adapter registration gate that enables only the Strands adapter and requires verified API/auth evidence plus conformance tests for future adapters and verify Hermes/OpenClaw are not advertised or selectable in release configuration.

## 4. React Native and Owned Native Foundation

- [ ] 4.1 Replace the Flutter application with a TypeScript React Native application, commit and own the directly buildable `mobile/ios/` and `mobile/android/` projects plus the iOS application/Share Extension targets and Android application/service configuration, and verify Xcode and Gradle development builds succeed without Expo Go or native-project regeneration.
- [x] 4.2 Build the shared TypeScript navigation, state, adaptive design system, accessible shell, and independent interface-language/reply-language settings with English, Vietnamese, and German resources and verify component tests change each preference independently on both platform configurations.
- [ ] 4.3 Implement typed domain models for sessions, shared context, conversations, events, approvals, tasks, consent receipts, and privacy records over the generated API types; add React Native Codegen specs under `mobile/src/native/specs/` and sanitized wrappers under `mobile/src/platform/`; and verify serialization fixtures and generated native bindings compile for Swift and Kotlin.
- [ ] 4.4 Implement the TypeScript storage boundary with Keychain/Keystore-backed native secret operations, SQLCipher-backed structured storage, app-private temporary-file lifecycle, and retention cleanup and verify tests never return raw session secrets to general JavaScript callers and delete expired/discarded working data while retaining explicitly saved records.
- [ ] 4.5 Build onboarding and privacy/settings surfaces with permission benefits, exact data scope, decline paths, pairing removal, local data inspection/deletion, and opt-in memory controls and verify React Native accessibility tests cover text scaling, semantics, and every permission skip path.
- [ ] 4.6 Add mobile CI gates for TypeScript type checking, unit/component tests, API and React Native Codegen drift, `xcodebuild` of the app and Share Extension, and Gradle builds of the app and service configuration and verify the gates exercise committed native projects rather than Expo Go.

## 5. Mobile Pairing and Session Lifecycle

- [ ] 5.1 Implement QR/device-code scanning and manual entry with backend identity and requested-capability review and verify no claim is submitted before local confirmation.
- [ ] 5.2 Implement authenticated API session creation, access renewal, rotation persistence, and logout/revocation handling and verify expired-token recovery and revoked-device UI tests pass without exposing credentials.
- [ ] 5.3 Implement local and remote device removal flows that clear secrets, cached events, and push registration and verify a removed phone cannot make an authenticated request.
- [ ] 5.4 Add privacy controls for inspecting/deleting conversations, documents, shares, and opt-in memory with disclosed remote effects and verify deletion integration tests remove the selected local and facade records.

## 6. Conversation, Voice, and Event Streaming

- [ ] 6.1 Build conversation list/detail/composer UI for text, images, files, and typed action cards and verify React Native component tests render incomplete, completed, failed, and retriable message states accessibly.
- [ ] 6.2 Implement SSE consumption with ordered sequence handling, last-event resume, polling fallback, and explicit completion semantics and verify reconnect tests neither duplicate fragments nor mark failed streams complete.
- [ ] 6.3 Implement user-driven voice-note recording, playback, review, deletion, and consented upload behind a typed React Native native-module interface and verify TypeScript and native tests upload no audio after microphone denial or cancellation.
- [ ] 6.4 Implement offline drafts and failed-send behavior that requires renewed consent for expired attachment uploads and verify airplane-mode integration tests preserve drafts without silent re-upload.
- [ ] 6.5 Add multilingual response rendering for facts, suggestions, warnings, uncertainties, and Markdown-safe text and verify mixed-language fixtures retain selected reply language and distinguish uncertain extraction.

## 7. Approvals, Push, Reminders, and Tasks

- [ ] 7.1 Implement the facade approval state machine, expiry/revocation, scoped decisions, immutable proposal data, and unique action keys and verify duplicate allow requests execute an effect at most once.
- [ ] 7.2 Build the unified mobile inbox for pending approvals, agent questions, drafts, tasks, and outcomes with origin and risk details and verify React Native component tests for status, filters, and deep links pass.
- [ ] 7.3 Integrate APNs/FCM registration through the owned Swift and Kotlin native projects with opaque event notifications and authenticated content fetch and verify native and service payload tests contain only event ID and non-sensitive category.
- [ ] 7.4 Implement allow, deny, and narrower-scope review flows with stale/expired outcome handling and verify no effect occurs before confirmation or after denial.
- [ ] 7.5 Implement reviewed local reminder/task creation through typed Swift UserNotifications/EventKit and Kotlin notification/calendar modules with editable title, date/time, notification, and destination and verify native tests create only the final user-confirmed values.
- [ ] 7.6 Restrict executable action cards to the explicit initial allowlist and verify unknown or prohibited classes fail closed in both facade and TypeScript tests.

## 8. Cross-Platform Share Intake

- [x] 8.1 Define the TypeScript `ShareIntakePlatform` domain boundary, its React Native Codegen contract, and consent-receipt digest/expiry behavior and verify bridge fixtures reject undeclared metadata and changed payloads invalidate prior consent.
- [ ] 8.2 Implement the first-class Kotlin Android share receiver and staging module for text, URLs, images, screenshots, and PDFs and verify instrumentation tests stage only selected intent items without exposing unrelated metadata or sending them.
- [ ] 8.3 Implement the first-class Swift iOS Share Extension target and App Group handoff for text, URLs, images, screenshots, and PDFs and verify XCTest coverage stages only selected items, imports through explicit app review, and cleans cancelled shares.
- [ ] 8.4 Build the shared destination/purpose/content/redaction/retention review screen and verify confirm and cancel tests respectively send exactly approved parts or send nothing.
- [ ] 8.5 Implement bounded upload orchestration with consent expiry and failure recovery and verify a failed upload cannot retry after consent withdrawal without a new review.

## 9. Private Documents and OCR

- [x] 9.1 Define the TypeScript `DocumentCapturePlatform` domain interface and React Native Codegen OCR result contract, including page identity, text blocks, confidence, and cleanup lifecycle, and verify bridge contract tests reject native results containing undeclared raw metadata.
- [ ] 9.2 Implement the first-class Kotlin Android camera/import and on-device ML Kit OCR module and verify instrumentation/device tests extract fixture text while retaining source images locally by default.
- [ ] 9.3 Implement the first-class Swift iOS VisionKit/import and Vision OCR module and verify XCTest simulator/device coverage extracts fixture text while retaining source pages locally by default.
- [ ] 9.4 Build document page/text selection, sensitive-field preview, text-only default, per-document consent, and local discard/save controls and verify declined disclosure sends no text or image and clears working cache.
- [ ] 9.5 Implement service document explanation/translation with issuer, amount, deadline, warnings, facts, suggestions, and uncertainty and verify deterministic fixtures never promote low-confidence values to facts.
- [ ] 9.6 Connect document results to approval-only reminder/task drafts and verify invoice and insurance-letter tests produce no payment, submission, signature, or third-party transmission.

## 10. Safe Native Integrations

- [x] 10.1 Define narrow TypeScript domain interfaces and React Native Codegen contracts for credential handoff, external navigation, local reminders, and app capability checks and verify generated bridge tests cannot carry password, OTP, recovery, card, or bank values.
- [ ] 10.2 Implement first-class Kotlin Android Credential Manager and Swift iOS AuthenticationServices/Password AutoFill handoff modules and verify native tests return only bounded completion/cancellation status to the JavaScript runtime and never return credential values.
- [ ] 10.3 Implement confirmation-gated Kotlin Android intents and Swift iOS universal links/URL schemes with exact destination display and verify native and TypeScript tests issue no navigation request before the local confirmation tap.
- [ ] 10.4 Implement curated, user-enabled Kotlin Android capability booleans and configured Swift iOS integration/deep-link checks and verify bridge and network tests contain no package names or installed-app inventory.
- [x] 10.5 Add iOS current-context guidance for share sheet, screenshot/file import, direct integrations, and future browser extension availability and verify UI tests make no arbitrary-screen or overlay claim.

## 11. Android Screen Help Beta

- [ ] 11.1 Implement separate Screen Help onboarding, accessibility/overlay permission checks, beta labeling, decline behavior, and disable controls and verify declining leaves every shared app feature usable with no service or overlay running.
- [ ] 11.2 Implement the first-class Kotlin AccessibilityService short capture window and one-shot active-root read without event history or gesture APIs and verify events outside a bubble-tap session produce no retained snapshot or React Native event.
- [ ] 11.3 Implement Kotlin tree sanitization, bounds, password-node exclusion, sensitive-context/package suppression, and login/OTP safety guidance and verify unit fixtures never expose protected values, descendant text, or raw node trees across the Codegen boundary.
- [ ] 11.4 Implement the Kotlin floating overlay and bounded snapshot module plus the React Native local preview with app label/category, text count, redactions, screenshot state, send, and cancel and verify tapping cancel discards all working context.
- [ ] 11.5 Route approved sanitized context through the normal TypeScript consent/request contract with screenshot consent independent and off by default and verify bridge/network interception tests show minimized fields and no unapproved screenshot bytes.
- [ ] 11.6 Run Android accessibility, overlay, large-text, TalkBack, login, settings, credential-provider, and lifecycle device tests and verify Screen Help never taps, types, scrolls, submits, or captures in suppressed contexts.

## 12. AgentCore Infrastructure and Operations

- [ ] 12.1 Create the service container and CDK application for ECR, AgentCore Runtime, facade resources, logs with retention, and configuration references and verify image build and `cdk synth` succeed without account IDs or secrets in source.
- [ ] 12.2 Define least-privilege facade and runtime roles for only required invocation, data-store, memory, secret, and logging operations and verify policy assertions reject wildcard administrative and mobile control-plane access.
- [ ] 12.3 Store model, endpoint, push, signing, and environment configuration in Secrets Manager/SSM or deployment inputs and verify secret scanning finds no credentials in mobile binaries, source, fixtures, or generated artifacts.
- [ ] 12.4 Deploy a non-production stage in a confirmed AgentCore-supported region and verify signed paired-device requests receive correlated structured multilingual events through the facade.
- [ ] 12.5 Implement feature flags, API compatibility controls, observability, retention jobs, and rollback procedures and verify disabling a capability stops new use while revocation and deletion remain operational.

## 13. End-to-End Safety and Release Readiness

- [ ] 13.1 Build service/mobile end-to-end tests using React Native development or release builds with the real native modules for pairing, multilingual chat/voice, cross-platform share, OCR explanation, push approval, reminder creation, revocation, offline behavior, and Android Screen Help and verify the common suites pass on iOS and Android while Screen Help runs only on Android.
- [ ] 13.2 Run red-team tests for phishing, prompt injection, passwords, OTPs, cards, bank identifiers, health documents, mixed languages, and requests for every prohibited action and verify no forbidden data or executable action crosses a logged trust boundary.
- [ ] 13.3 Complete manual VoiceOver/TalkBack, large-text, permission-decline, offline, and low-confidence reviews with representative multilingual participants and record acceptance evidence for each capability spec.
- [ ] 13.4 Finalize privacy notice, data-flow and architecture diagrams, pairing/operator guide, platform capability disclosure, deletion/retention guide, and demo script and verify documentation matches implemented behavior and does not claim unverified Hermes/OpenClaw or iOS screen-inspection support.
- [ ] 13.5 Produce reproducible release builds directly from the committed `mobile/ios/` application/Share Extension targets and `mobile/android/` application/service configuration, plus a five-minute two-platform demo showing one shared workflow and Android Screen Help beta, and verify no Expo Go dependency, release checklists, dependency audits, secret scans, tests, and rollback rehearsal before tagging.
