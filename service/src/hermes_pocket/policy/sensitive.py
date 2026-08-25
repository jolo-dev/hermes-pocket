from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class SensitiveCategory(StrEnum):
    PASSWORD = "password"  # noqa: S105 - classification label, not a credential
    OTP = "otp"
    RECOVERY_CODE = "recovery_code"
    CARD = "card"
    BANK = "bank"


@dataclass(frozen=True, slots=True)
class Finding:
    category: SensitiveCategory
    start: int
    end: int


@dataclass(frozen=True, slots=True)
class SanitizationResult:
    text: str
    categories: tuple[SensitiveCategory, ...]
    redaction_count: int


class SensitiveDataRejected(ValueError):
    def __init__(self, categories: tuple[SensitiveCategory, ...] = ()) -> None:
        self.categories = categories
        super().__init__("Sensitive content could not be safely minimized.")


_LABELED_PATTERNS: tuple[tuple[SensitiveCategory, re.Pattern[str]], ...] = (
    (
        SensitiveCategory.PASSWORD,
        re.compile(
            r"\b(?:password|passphrase|passcode)\s*(?:is|:|=)\s*[\"']?(?P<value>[^\s\"']{4,128})",
            re.IGNORECASE,
        ),
    ),
    (
        SensitiveCategory.OTP,
        re.compile(
            r"\b(?:otp|one[- ]time (?:password|code)|verification code)"
            r"\s*(?:is|:|=)?\s*(?P<value>\d{4,8})\b",
            re.IGNORECASE,
        ),
    ),
    (
        SensitiveCategory.RECOVERY_CODE,
        re.compile(
            r"\b(?:recovery|backup) code\s*(?:is|:|=)?\s*"
            r"(?P<value>[A-Z0-9]+(?:-[A-Z0-9]+){1,15})\b",
            re.IGNORECASE,
        ),
    ),
    (
        SensitiveCategory.CARD,
        re.compile(
            r"\b(?:cvv|cvc|card security code)\s*(?:is|:|=)?\s*(?P<value>\d{3,4})\b",
            re.IGNORECASE,
        ),
    ),
    (
        SensitiveCategory.BANK,
        re.compile(
            r"\b(?:bank )?account(?: number)?\s*(?:is|:|=)?\s*(?P<value>\d{6,34})\b",
            re.IGNORECASE,
        ),
    ),
)
_CARD_CANDIDATE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_IBAN_CANDIDATE = re.compile(r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b")
_UNBOUNDED_SECRET_ASSIGNMENT = re.compile(
    r"\b(?:password|passphrase|passcode|otp|recovery code|backup code|cvv|cvc|account number)"
    r"\s*[:=]\s*[^\r\n]{129,}",
    re.IGNORECASE,
)


def _passes_luhn(value: str) -> bool:
    digits = [int(character) for character in value]
    parity = len(digits) % 2
    checksum = 0
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
    return checksum % 10 == 0


def _valid_iban(value: str) -> bool:
    compact = value.replace(" ", "")
    if not 15 <= len(compact) <= 34:
        return False
    rearranged = compact[4:] + compact[:4]
    numeric = "".join(
        str(ord(character) - 55) if character.isalpha() else character for character in rearranged
    )
    return int(numeric) % 97 == 1


def _find_sensitive_spans(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for category, pattern in _LABELED_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding(category, match.start("value"), match.end("value")))

    for match in _CARD_CANDIDATE.finditer(text):
        compact = re.sub(r"[ -]", "", match.group())
        if 13 <= len(compact) <= 19 and _passes_luhn(compact):
            findings.append(Finding(SensitiveCategory.CARD, match.start(), match.end()))

    for match in _IBAN_CANDIDATE.finditer(text.upper()):
        if _valid_iban(match.group()):
            findings.append(Finding(SensitiveCategory.BANK, match.start(), match.end()))

    return sorted(findings, key=lambda finding: (finding.start, -finding.end))


def sanitize_for_model(text: str) -> SanitizationResult:
    if "\x00" in text or _UNBOUNDED_SECRET_ASSIGNMENT.search(text):
        raise SensitiveDataRejected()

    findings = _find_sensitive_spans(text)
    if len(findings) > 20:
        raise SensitiveDataRejected(tuple(sorted({item.category for item in findings})))
    if not findings:
        return SanitizationResult(text=text, categories=(), redaction_count=0)

    output: list[str] = []
    categories: set[SensitiveCategory] = set()
    cursor = 0
    redaction_count = 0
    for finding in findings:
        if finding.start < cursor:
            categories.add(finding.category)
            continue
        output.append(text[cursor : finding.start])
        output.append(f"[REDACTED:{finding.category.value.upper()}]")
        categories.add(finding.category)
        cursor = finding.end
        redaction_count += 1
    output.append(text[cursor:])
    return SanitizationResult(
        text="".join(output),
        categories=tuple(sorted(categories)),
        redaction_count=redaction_count,
    )
