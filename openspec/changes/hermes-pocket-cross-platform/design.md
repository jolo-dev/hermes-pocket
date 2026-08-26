## Context

See `proposal.md` for motivation and the capability specs for observable behavior. This is a greenfield cross-platform product with three trust zones: the user's phone, a mobile-facing authenticated service, and the selected agent runtime/backend. Mobile operating systems expose materially different context APIs: Android can offer a disclosed AccessibilityService and overlay, while iOS cannot inspect arbitrary other apps or display a system-wide agent overlay.

The initial backend is a Python Strands agent on Bedrock AgentCore Runtime, but the mobile protocol must not encode Strands, Hermes, OpenClaw, or AWS implementation details. All screen, share, and document content is untrusted and may contain secrets or prompt injection. Safety rules therefore cannot depend solely on model instructions.

## Goals / Non-Goals

**Goals:**

- Share one product model, design system, local persistence model, API client, and approval experience across iOS and Android.
- Isolate OS-specific behavior behind narrow TypeScript interfaces and typed React Native native-module contracts whose Swift and Kotlin implementations return sanitized domain values.
- Enforce consent, data minimization, prohibited-data filtering, and action restrictions before invoking any agent backend.
- Support revocable device pairing and authenticated event delivery without distributing cloud infrastructure credentials.
- Make backend substitution possible only through a tested adapter contract with invariant facade policy.
- Preserve request correlation and idempotency across mobile, facade, adapter, and asynchronous approval flows.

**Non-Goals:**

- Feature parity for arbitrary current-screen inspection on iOS.
- A password vault, AutofillService, credential reader, autonomous phone operator, or general accessibility event recorder.
- Autonomous payments, purchases, contracts, claims, messages, account changes, form submission, or cross-app typing.
- Direct mobile access to AWS control-plane APIs, AgentCore credentials, or backend-private state databases.
- An initial browser extension or unverified Hermes/OpenClaw adapter; the first release leaves extension points but does not claim those integrations.

## Decisions

### 1. React Native owns shared product behavior while native projects remain first-class

Create a `mobile/` React Native application using TypeScript for navigation, state, generated API contracts, conversation rendering, approvals, privacy controls, and the shared document workflow. Use a React Native setup with committed and project-owned `mobile/ios/` and `mobile/android/` projects as the source of truth for native builds, targets, entitlements, manifests, signing inputs, and configuration. Expo Go is not an allowed development or acceptance environment because it cannot contain the required native targets and services. Expo development builds or EAS build tooling may be added only if the owned native projects, targets, and configuration remain committed, directly buildable, and reviewable without regeneration.

Swift and Kotlin modules are first-class product components, not incidental plugins:

| TypeScript boundary | Android implementation | iOS implementation |
|---|---|---|
| Share intake | Kotlin intent receiver and staging module | Swift Share Extension and App Group handoff |
| Document capture/OCR | Kotlin camera/import and ML Kit module | Swift VisionKit/import and Vision module |
| Credential handoff | Kotlin Credential Manager module | Swift AuthenticationServices/Password AutoFill module |
| Notifications/reminders | Kotlin notification/calendar module | Swift UserNotifications/EventKit module as approved |
| External destination | Kotlin intent/deep-link resolver | Swift universal-link/URL-scheme resolver |
| Screen help | Kotlin AccessibilityService, overlay, and snapshot module | Unsupported; explicit-share guidance |

React Native Codegen specifications define the typed native-module surface where synchronous app/native communication is required. TypeScript domain wrappers expose only bounded, sanitized tagged results and status codes. The iOS Share Extension stages approved items through the App Group for explicit app intake rather than attempting to run the shared application in the extension. Raw credential-provider results, raw accessibility node trees, continuous accessibility events, and unrestricted platform metadata never enter the JavaScript runtime.

Alternatives considered: separate Compose and SwiftUI apps would maximize native UI control but duplicate most product and safety behavior. Flutter would also share UI, but React Native aligns the mobile domain and generated API client with the repository's TypeScript contracts while retaining owned native escape hatches. Expo managed workflow and Expo Go are rejected because the required Share Extension, App Group, AccessibilityService, overlay, credential, Vision, and ML Kit targets must remain committed and directly owned.

### 2. Explicit sharing is the cross-platform context baseline

The common context model is a user-selected `SharedContext` containing one or more typed parts: text, URL, image, PDF, screenshot, or voice note. Intake stages content locally, then opens a review screen with destination, purpose, selected parts, redactions, and retention choice. A consent receipt binds approval to content digests, request purpose, destination session, and a short validity window; changed content requires renewed consent.

Android Screen Help is a separate optional source that produces the same sanitized context model only after a bubble tap and preview. iOS surfaces share sheet, screenshot import, direct integration, and future browser-extension options rather than pretending system-wide access exists.

Alternative considered: treating Android accessibility capture as the primary product would make iOS secondary and increase policy/surveillance risk. Explicit sharing provides credible value and equivalent safety on both platforms.

### 3. A versioned authenticated facade owns policy and adapters

The mobile app communicates only with a FastAPI facade over TLS. The facade exposes versioned resources for:

- pairing claim, token rotation, device inspection, and revocation;
- conversations, message submission, attachment/context upload, and response events;
- approvals, resolution, tasks, and event synchronization;
- privacy data inspection, memory consent, and deletion.

The facade authenticates the device, validates contracts, applies rate/size limits, redacts content, enforces capabilities, assigns correlation IDs, and persists mobile workflow state. It then calls an `AgentBackend` interface with operations equivalent to `pair`, `send_message`, `list_approvals`, `resolve_approval`, `list_tasks`, and `revoke_device`.

The first adapter wraps Strands and AgentCore Runtime. Future Hermes/OpenClaw adapters are enabled only after remote API and authentication behavior are verified against contract and safety suites. Adapters cannot register tools or action classes outside a facade-controlled allowlist.

Alternative considered: connecting mobile directly to AgentCore or embedding backend-specific clients would expose cloud credentials, couple releases to one runtime, and allow adapter-specific policy drift.

### 4. Contracts use generated typed envelopes and an event stream

Canonical OpenAPI and JSON Schema documents under `contracts/` are versioned independently of backend adapters. Deterministic generation produces the TypeScript request, response, error, and event types plus the mobile API client under `mobile/src/generated/api/`; generated files are never edited by hand. The Python service validates the same schemas, and shared fixtures exercise both Python serialization and TypeScript parsing. CI regenerates contracts and fails on a dirty diff, incompatible schema changes, TypeScript compile failures, or fixture disagreement.

Every command contains `request_id`, `device_session_id`, `policy_version`, locale/reply preferences, and an allowlisted payload. Every asynchronous result uses an event envelope with monotonically ordered conversation/event sequence, event type, resource identifier, and correlation ID. Native bridge contracts are separate from network contracts: React Native Codegen specs live under `mobile/src/native/specs/`, while wrappers under `mobile/src/platform/` map generated native results into the same sanitized domain model. Swift and Kotlin tests verify that undeclared fields and prohibited raw values cannot cross those boundaries.

SSE is the default foreground stream because responses are server-to-client and reconnection can use the last event identifier. A polling sync endpoint is the correctness fallback. Push through APNs/FCM is only a wake-up hint containing an opaque event ID and category; full content is fetched after authentication. WebSocket support is deferred until bidirectional realtime requirements justify it.

### 5. Deterministic policy wraps every model invocation

Safety enforcement is a pipeline rather than a prompt convention:

1. Parse against a strict field allowlist and bounded payload sizes.
2. Classify source and context, rejecting forbidden contexts and undeclared fields.
3. Redact password-, OTP-, recovery-, card-, and bank-data patterns and reject when safe removal cannot be guaranteed.
4. Bind user intent and approved capabilities separately from untrusted content.
5. Construct the model request with untrusted blocks clearly delimited and no prohibited tools.
6. Validate structured output, block forbidden action classes, and downgrade unsupported confidence claims.
7. Emit privacy-safe diagnostics containing identifiers and categories, not content.

The agent system instructions require the selected reply language, structured facts/suggestions/uncertainties, source-grounding, and prompt-injection resistance. These improve output quality but do not replace deterministic checks.

Alternative considered: model-only moderation is insufficient because malicious shared content can target the model and model output is probabilistic.

### 6. Data is classified by location and retention

| Data | Default location | Remote eligibility |
|---|---|---|
| Password, OTP, recovery code, card/bank data | Never intentionally captured | Never |
| Share/document source | App-encrypted local working storage | One request only with item consent |
| OCR text | Device | Redacted selection with item consent |
| Android accessibility text | Memory during active request | Minimized/redacted selection after preview |
| Redacted screenshot | Ephemeral local cache | One request only with explicit screenshot consent |
| Conversation/task metadata | Encrypted local database and facade | Required for selected workflow |
| Reminder summary memory | Device by default | Optional, inspectable, expiring opt-in |
| Device session credential | Keychain/Keystore-backed storage | Authentication endpoints only |

Use an owned TypeScript storage boundary backed by iOS Keychain and Android Keystore native access for session secrets, plus a SQLCipher-backed local database adapter for retained structured records. Secret-returning native APIs are not exposed to general JavaScript callers; the session layer receives only the bounded operations it needs. Temporary files are allocated in app-private storage, referenced by lifecycle state, and deleted after save/discard or consent expiry. The facade stores only workflow data required for synchronization and configured retention. Raw source retention is off by default.

### 7. Approvals are an idempotent state machine

An approval records immutable proposal details, source agent, requested capability, risk class, disclosure summary, expiry, and allowed scopes. Resolution transitions from `pending` to one of `allowed`, `denied`, `expired`, `revoked`, or `superseded`. A unique action key makes duplicate allows return the recorded result rather than repeat the effect.

The initial executable allowlist is intentionally narrow: create a reviewed local reminder/task, open a confirmed destination, or grant a bounded backend read/tool scope that is not in a prohibited class. Draft text can be copied or exported by a deliberate user action, but the agent cannot send it. The facade rejects prohibited classes before mobile rendering, and the client also fails closed for unknown classes.

Alternative considered: generic tool-call approval cards are flexible but unsafe because a new backend tool could become executable without coordinated product policy.

### 8. Pairing uses one-time claims and revocable device sessions

An owner-controlled deployment creates a random, short-lived, single-use claim containing only a facade URL, backend identity fingerprint, and claim secret. The app displays identity and requested capabilities before claiming. Successful claim creates a device record and returns a short-lived access token plus rotatable device-bound renewal material stored in Keychain/Keystore-backed storage.

The owner and phone can revoke the device. Revocation invalidates renewal material, rejects API calls, stops push association, and propagates to the active adapter. No shared API key, AWS credential, or AgentCore credential is embedded in the application or QR payload.

Alternative considered: a long-lived bearer API key is simpler but is difficult to scope, rotate, and revoke per lost device.

### 9. Documents follow a local-first staged pipeline

Capture/import produces local pages, platform OCR output, and confidence metadata behind one TypeScript domain interface implemented by the Swift Vision/VisionKit and Kotlin ML Kit native modules. The review pipeline identifies candidate sensitive values and lets the user include/exclude pages, images, and text. Text-only is the default remote option. The service returns a structured explanation with facts, suggestions, warnings, and uncertainties; any reminder is created as an approval draft.

Originals and working pages remain local unless explicitly selected for one request. If upload fails, the consent receipt is not reused silently. Saved local history stores only user-selected source/derived content; discard removes the working set.

### 10. Android Screen Help has a short-lived capture session

The AccessibilityService is dormant as a data source until a local bubble-tap nonce starts a short capture window. It reads the active root once, skips Hermes Pocket, settings, permission, credential-provider, and configured sensitive packages/windows, excludes password nodes and descendants, sanitizes bounded text, and immediately drops node references.

The preview reports app label/category, counts, redactions, and screenshot state. A separate send tap creates the normal consent receipt. Screenshot capture is independent and off by default. The service retains no event history and exposes no gesture, typing, submission, raw-node, or continuous-event API to TypeScript or the backend. Disabling Screen Help tears down the overlay and clears pending snapshots.

### 11. AgentCore deployment is server-side and least privilege

Package the FastAPI/Strands runtime as a container and deploy it to a confirmed AgentCore-supported region. Infrastructure defines the image repository, runtime execution role, bounded model invocation permissions, logs with retention, secrets/parameters, and the authenticated mobile facade. Optional AgentCore Memory receives only policy-approved opt-in summaries under explicit retention.

The runtime role cannot administer mobile identities or cloud infrastructure. The facade identity can invoke only the configured runtime and required data stores. Infrastructure configuration supplies account, region, model, endpoints, and push credentials; none are hard-coded in source or mobile binaries.

### 12. Testing and release acceptance include shared and native layers

The mobile test strategy has explicit boundaries. TypeScript unit and component tests cover domain policy, generated contract fixtures, navigation, consent, redaction summaries, accessibility semantics, and state handling. Swift XCTest suites cover the Share Extension/App Group handoff, Vision/VisionKit, AuthenticationServices, notification/reminder behavior, and native boundary sanitization. Kotlin unit and instrumentation suites cover share intents, ML Kit, Credential Manager, AccessibilityService suppression, overlay lifecycle, and native boundary sanitization.

CI builds the committed iOS application and Share Extension targets with `xcodebuild`, builds the committed Android application and service configuration with Gradle, type-checks TypeScript, checks React Native Codegen and API generation for drift, and runs service contract tests. End-to-end acceptance runs against development or release builds containing the real native modules, never Expo Go. The release matrix requires common pairing, conversation, sharing, document, approval, privacy, revocation, offline, localization, and accessibility scenarios on both platforms; Android Screen Help scenarios run only on Android, while iOS acceptance instead verifies honest share/import guidance and absence of arbitrary screen inspection or overlay claims.

## Risks / Trade-offs

- [Accessibility APIs can be perceived as surveillance and face store-policy restrictions] -> Make Screen Help optional, user-triggered, locally previewed, independently disableable, and initially distribute through controlled test channels pending policy review.
- [Pattern redaction can miss secrets or over-redact useful values] -> Combine node metadata, allowlists, validated detectors, conservative rejection, red-team fixtures, and transparent redaction summaries; never promise perfect classification.
- [Push providers observe delivery metadata] -> Send opaque identifiers only, fetch content through the authenticated facade, and allow notification previews to be disabled.
- [React Native packages or native bridges may leak raw platform data into shared policy] -> Keep boundaries narrow, Codegen-typed, sanitized, and replaceable; test Swift/Kotlin boundary outputs and enforce final policy at both facade and TypeScript domain layers rather than inside third-party packages.
- [Generated network or native types can drift from runtime behavior] -> Keep canonical schemas and Codegen specs in source, regenerate deterministically in CI, fail on diffs or fixture disagreement, and require coordinated compatibility review for schema changes.
- [Optional Expo/EAS tooling could make generated native state authoritative] -> Treat committed `ios/` and `android/` projects as source, prohibit Expo Go, review native diffs, and require direct Xcode and Gradle builds in release acceptance.
- [AgentCore or model availability can interrupt cloud assistance] -> Preserve local capture/OCR and drafts, expose explicit offline/error states, and use resumable event synchronization without silent re-upload.
- [Adapter abstraction can hide incompatible backend semantics] -> Keep a compact required contract, require conformance/safety tests, and do not enable or market an adapter until authentication and action semantics are verified.
- [Multilingual output can be fluent but inaccurate] -> Preserve source excerpts where safe, separate facts from suggestions, expose confidence/uncertainty, and test representative Vietnamese, German, English, and mixed-language fixtures with speakers.
- [Encrypted local storage does not protect an unlocked compromised device] -> Minimize retention, use OS secure storage and device authentication where appropriate, provide deletion controls, and document the trust boundary.

## Migration Plan

There is no existing application data to migrate. Delivery is staged to reduce security and platform risk:

1. Preserve the established contracts, threat model, deterministic policy, facade, and adapter conformance tests, then add deterministic TypeScript API generation and shared Python/TypeScript fixture gates.
2. Replace the Flutter shell with the React Native TypeScript application and committed, directly buildable iOS and Android projects; establish Codegen-typed native boundaries before feature UI migration.
3. Deliver pairing, multilingual chat/voice, approvals, privacy controls, and event synchronization on both platforms using development builds that contain the owned native modules.
4. Implement and test first-class Swift Share Extension/App Group/Vision/AuthenticationServices modules and Kotlin share/ML Kit/Credential Manager modules, then add shared review and document workflows.
5. Add notification/reminder and confirmed external-navigation modules, then enable Android Screen Help only in an opt-in beta after sanitizer, device, accessibility, overlay, and policy tests pass.
6. Deploy the Strands runtime and facade to a non-production AgentCore stage, complete the shared/native/end-to-end acceptance matrix, then promote immutable artifacts built from the committed native projects.

Each stage is feature-flagged at the facade and client capability level. Rollback disables the affected capability, revokes incompatible API versions if necessary, and restores the prior mobile/runtime artifact without migrating prohibited raw content. Pairing revocation and local deletion remain available during rollback.

## Open Questions

- Which AgentCore-supported region and model will the deployment owner select? This remains environment configuration and does not alter the mobile or adapter contracts.
- Which APNs/FCM project identifiers and release signing identities will be used? These are deployment inputs and do not change push payload behavior.
- What default retention duration will be offered for opt-in non-secret memory? The implementation will enforce a bounded configurable value and expose the selected duration before consent.
