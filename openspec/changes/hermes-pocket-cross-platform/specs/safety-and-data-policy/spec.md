## Purpose

Enforce privacy and safety invariants outside model judgment so shared content cannot leak secrets, override policy, or authorize consequential actions.

## ADDED Requirements

### Requirement: Prohibited sensitive data
The system MUST NOT intentionally capture, transmit, store, include in memory, or log passwords, OTPs, recovery codes, card numbers or security codes, or bank-account identifiers, even when a user or untrusted document requests it.

#### Scenario: Request contains a card number
- **WHEN** client or server validation detects card data in an outgoing payload
- **THEN** the value is removed or the request is rejected before agent invocation and the sensitive value is absent from logs and error responses

#### Scenario: User asks the agent to remember an OTP
- **WHEN** the user requests storage of a one-time code
- **THEN** the system refuses the request and creates no local or remote memory entry containing the code

### Requirement: Deterministic data minimization
The system SHALL apply deterministic field allowlists, size limits, sensitive-value detection, and redaction before model invocation and SHALL reject unbounded screen, accessibility, installed-app, or document dumps.

#### Scenario: Unknown request field is submitted
- **WHEN** a mobile request includes an undeclared field containing raw device context
- **THEN** contract validation rejects the request without forwarding that field to the backend adapter

### Requirement: Untrusted-content isolation
Screen text, shared webpages, messages, OCR text, and documents SHALL be labeled and handled as untrusted data, SHALL be separated from user intent and system policy, and SHALL NOT be able to add tools, change policy, or authorize an action.

#### Scenario: Document contains prompt injection
- **WHEN** OCR text says to ignore prior instructions and send the document elsewhere
- **THEN** the system treats the sentence as document content, does not send the document, and continues only with the user's approved explanation or translation purpose

### Requirement: Prohibited autonomous actions
The system SHALL NOT execute or offer approval as a means to execute payments, purchases, contract acceptance, claim submission, form submission, credential entry, cross-app typing, account changes, or message sending in the initial product.

#### Scenario: User requests bill payment
- **WHEN** the user asks the agent to pay an identified bill
- **THEN** the system refuses payment execution, may explain the bill, and may offer a user-reviewed reminder

#### Scenario: Model returns prohibited tool call
- **WHEN** a backend response includes a prohibited action or tool invocation
- **THEN** deterministic policy blocks it and returns a safe refusal or explanation without exposing it as executable

### Requirement: Facts, suggestions, and uncertainty
Agent responses SHALL distinguish source-grounded facts from suggestions, SHALL state when source content is unavailable or redacted, and SHALL mark low-confidence extracted values as requiring verification rather than inventing certainty.

#### Scenario: Source text is mostly redacted
- **WHEN** redaction leaves insufficient content to explain a document reliably
- **THEN** the response states the limitation and asks for safe clarification without reconstructing redacted values

### Requirement: Correlated privacy-safe diagnostics
Service and mobile diagnostics SHALL use request identifiers and coarse event metadata, SHALL exclude user content and prohibited sensitive data by default, and SHALL require explicit opt-in before collecting additional diagnostic detail.

#### Scenario: Agent invocation fails
- **WHEN** the runtime returns an internal error
- **THEN** logs contain a correlation identifier and error category but no conversation text, document text, credentials, or raw screen content
