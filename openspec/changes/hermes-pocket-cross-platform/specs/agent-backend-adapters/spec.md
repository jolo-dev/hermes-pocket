## Purpose

Define a stable mobile-facing contract that supports the initial Strands service and permits later agent backends only after their APIs and authentication models are verified.

## ADDED Requirements

### Requirement: Versioned mobile facade
The system SHALL expose a versioned, authenticated mobile API for pairing, conversation messages and event streams, context sharing, approval resolution, task retrieval, events, and device revocation.

#### Scenario: Unsupported API version is requested
- **WHEN** a client requests an unsupported contract version
- **THEN** the facade returns a structured compatibility error without forwarding the request to an agent backend

### Requirement: Backend-neutral adapter behavior
Every backend adapter SHALL implement equivalent operations for pairing/session establishment, message streaming, approval listing and resolution, task listing, and device revocation, and SHALL translate backend-specific errors into the mobile contract.

#### Scenario: Backend stream fails
- **WHEN** the selected backend terminates a response stream with an error
- **THEN** the adapter emits a structured failure event with a request correlation identifier and does not fabricate a completion event

### Requirement: Initial Strands backend
The first production adapter SHALL invoke a policy-constrained Strands agent hosted on Bedrock AgentCore Runtime through the server-side facade and SHALL return structured content and action proposals supported by the mobile contract.

#### Scenario: Mobile request reaches AgentCore
- **WHEN** an authenticated paired device sends an allowed conversation request
- **THEN** the facade invokes the configured runtime server-side and returns correlated response events without exposing AWS credentials to the device

### Requirement: Verified compatibility claims
The product SHALL identify Hermes or OpenClaw support only when an adapter uses a documented or independently verified remote API and authentication contract; otherwise the integration SHALL remain disabled and described as planned or experimental.

#### Scenario: OpenClaw remote contract is unverified
- **WHEN** no verified OpenClaw API and authentication contract has been approved
- **THEN** released clients do not offer an operational OpenClaw pairing option or claim compatibility

### Requirement: Adapter policy invariance
Changing the selected backend SHALL NOT weaken sensitive-data filtering, user consent, prohibited-action enforcement, event authentication, or audit correlation required by the mobile facade.

#### Scenario: Adapter proposes an unsupported action
- **WHEN** any adapter returns a payment or credential-entry action
- **THEN** the facade rejects the action before it is exposed as approvable to the client
