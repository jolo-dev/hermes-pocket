## Context

See `proposal.md` for motivation and the capability specs for observable behavior. This is a greenfield cross-platform product with three trust zones: the user's phone, a mobile-facing authenticated service, and the selected agent runtime/backend. Mobile operating systems expose materially different context APIs: Android can offer a disclosed AccessibilityService and overlay, while iOS cannot inspect arbitrary other apps or display a system-wide agent overlay.

The initial backend is a Python Strands agent on Bedrock AgentCore Runtime, but the mobile protocol must not encode Strands, Hermes, OpenClaw, or AWS implementation details. All screen, share, and document content is untrusted and may contain secrets or prompt injection. Safety rules therefore cannot depend solely on model instructions.

## Goals / Non-Goals

**Goals:**

- Share one product model, design system, local persistence model, API client, and approval experience across iOS and Android.
- Isolate OS-specific behavior behind narrow Dart interfaces whose native implementations return sanitized domain values.
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

### 1. Flutter owns shared product behavior

Create a `mobile/` Flutter application using Dart for navigation, state, API contracts, conversation rendering, approvals, privacy controls, and shared document workflow. Riverpod and GoRouter provide explicit state and routing boundaries. Adaptive Material/Cupertino components preserve platform conventions without maintaining two application implementations.

Native modules are limited to operations the OS must own:

| Dart boundary | Android implementation | iOS implementation |
|---|---|---|
| Share intake | Intent receiver | Share Extension |
| Document capture/OCR | Camera/ML Kit | VisionKit/Vision |
| Credential handoff | Credential Manager | AuthenticationServices/Password AutoFill |
| Notifications/reminders | Android notification/calendar APIs | UserNotifications/EventKit as approved |
| External destination | Intent/deep-link resolver | Universal link/URL scheme resolver |
| Screen help | AccessibilityService and overlay plugin | Unsupported; explicit-share guidance |

Platform channels return typed, sanitized results and status codes. Raw credential-provider results and continuous accessibility events never enter Dart.

Alternatives considered: separate Compose and SwiftUI apps would maximize native control but duplicate most product and safety behavior; React Native offers similar sharing but does not reduce the required native security modules. Flutter is selected for one polished shared UI and mature native escape hatches.

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

### 4. Contracts use typed envelopes and an event stream

JSON contracts are versioned independently of backend adapters. Every command contains `request_id`, `device_session_id`, `policy_version`, locale/reply preferences, and an allowlisted payload. Every asynchronous result uses an event envelope with monotonically ordered conversation/event sequence, event type, resource identifier, and correlation ID.

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

Use `flutter_secure_storage` for session secrets and a SQLCipher-backed local database for retained structured records. Temporary files are allocated in app-private storage, referenced by lifecycle state, and deleted after save/discard or consent expiry. The facade stores only workflow data required for synchronization and configured retention. Raw source retention is off by default.

### 7. Approvals are an idempotent state machine

An approval records immutable proposal details, source agent, requested capability, risk class, disclosure summary, expiry, and allowed scopes. Resolution transitions from `pending` to one of `allowed`, `denied`, `expired`, `revoked`, or `superseded`. A unique action key makes duplicate allows return the recorded result rather than repeat the effect.

The initial executable allowlist is intentionally narrow: create a reviewed local reminder/task, open a confirmed destination, or grant a bounded backend read/tool scope that is not in a prohibited class. Draft text can be copied or exported by a deliberate user action, but the agent cannot send it. The facade rejects prohibited classes before mobile rendering, and the client also fails closed for unknown classes.

Alternative considered: generic tool-call approval cards are flexible but unsafe because a new backend tool could become executable without coordinated product policy.

### 8. Pairing uses one-time claims and revocable device sessions

An owner-controlled deployment creates a random, short-lived, single-use claim containing only a facade URL, backend identity fingerprint, and claim secret. The app displays identity and requested capabilities before claiming. Successful claim creates a device record and returns a short-lived access token plus rotatable device-bound renewal material stored in Keychain/Keystore-backed storage.

The owner and phone can revoke the device. Revocation invalidates renewal material, rejects API calls, stops push association, and propagates to the active adapter. No shared API key, AWS credential, or AgentCore credential is embedded in the application or QR payload.

Alternative considered: a long-lived bearer API key is simpler but is difficult to scope, rotate, and revoke per lost device.

### 9. Documents follow a local-first staged pipeline

Capture/import produces local pages, platform OCR output, and confidence metadata behind one Dart interface. The review pipeline identifies candidate sensitive values and lets the user include/exclude pages, images, and text. Text-only is the default remote option. The service returns a structured explanation with facts, suggestions, warnings, and uncertainties; any reminder is created as an approval draft.

Originals and working pages remain local unless explicitly selected for one request. If upload fails, the consent receipt is not reused silently. Saved local history stores only user-selected source/derived content; discard removes the working set.

### 10. Android Screen Help has a short-lived capture session

The AccessibilityService is dormant as a data source until a local bubble-tap nonce starts a short capture window. It reads the active root once, skips Hermes Pocket, settings, permission, credential-provider, and configured sensitive packages/windows, excludes password nodes and descendants, sanitizes bounded text, and immediately drops node references.

The preview reports app label/category, counts, redactions, and screenshot state. A separate send tap creates the normal consent receipt. Screenshot capture is independent and off by default. The service retains no event history and exposes no gesture, typing, or submission API to Dart or the backend. Disabling Screen Help tears down the overlay and clears pending snapshots.

### 11. AgentCore deployment is server-side and least privilege

Package the FastAPI/Strands runtime as a container and deploy it to a confirmed AgentCore-supported region. Infrastructure defines the image repository, runtime execution role, bounded model invocation permissions, logs with retention, secrets/parameters, and the authenticated mobile facade. Optional AgentCore Memory receives only policy-approved opt-in summaries under explicit retention.

The runtime role cannot administer mobile identities or cloud infrastructure. The facade identity can invoke only the configured runtime and required data stores. Infrastructure configuration supplies account, region, model, endpoints, and push credentials; none are hard-coded in source or mobile binaries.

## Risks / Trade-offs

- [Accessibility APIs can be perceived as surveillance and face store-policy restrictions] -> Make Screen Help optional, user-triggered, locally previewed, independently disableable, and initially distribute through controlled test channels pending policy review.
- [Pattern redaction can miss secrets or over-redact useful values] -> Combine node metadata, allowlists, validated detectors, conservative rejection, red-team fixtures, and transparent redaction summaries; never promise perfect classification.
- [Push providers observe delivery metadata] -> Send opaque identifiers only, fetch content through the authenticated facade, and allow notification previews to be disabled.
- [Cross-platform plugins may leak behavior into shared policy] -> Keep plugins narrow, typed, and replaceable; enforce final policy at both facade and domain layers rather than inside third-party plugins.
- [AgentCore or model availability can interrupt cloud assistance] -> Preserve local capture/OCR and drafts, expose explicit offline/error states, and use resumable event synchronization without silent re-upload.
- [Adapter abstraction can hide incompatible backend semantics] -> Keep a compact required contract, require conformance/safety tests, and do not enable or market an adapter until authentication and action semantics are verified.
- [Multilingual output can be fluent but inaccurate] -> Preserve source excerpts where safe, separate facts from suggestions, expose confidence/uncertainty, and test representative Vietnamese, German, English, and mixed-language fixtures with speakers.
- [Encrypted local storage does not protect an unlocked compromised device] -> Minimize retention, use OS secure storage and device authentication where appropriate, provide deletion controls, and document the trust boundary.

## Migration Plan

There is no existing application data to migrate. Delivery is staged to reduce security and platform risk:

1. Establish contracts, threat model, deterministic policy, facade, and adapter conformance tests.
2. Deliver pairing, multilingual chat/voice, approvals, and event synchronization on both platforms.
3. Add share intake, local document OCR, disclosure review, and reminder drafts on both platforms.
4. Add credential handoff, notifications, and confirmed external navigation through narrow native modules.
5. Enable Android Screen Help only in an opt-in beta after sanitizer, device, accessibility, and policy tests pass.
6. Deploy the Strands runtime and facade to a non-production AgentCore stage, complete end-to-end safety tests, then promote immutable artifacts.

Each stage is feature-flagged at the facade and client capability level. Rollback disables the affected capability, revokes incompatible API versions if necessary, and restores the prior mobile/runtime artifact without migrating prohibited raw content. Pairing revocation and local deletion remain available during rollback.

## Open Questions

- Which AgentCore-supported region and model will the deployment owner select? This remains environment configuration and does not alter the mobile or adapter contracts.
- Which APNs/FCM project identifiers and release signing identities will be used? These are deployment inputs and do not change push payload behavior.
- What default retention duration will be offered for opt-in non-secret memory? The implementation will enforce a bounded configurable value and expose the selected duration before consent.
