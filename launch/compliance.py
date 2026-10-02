import os
import re
from pathlib import Path

from schemas.compliance import ComplianceReport


REQUIRED_PAGES = {
    "home": "src/app/page.tsx",
    "pricing": "src/app/pricing/page.tsx",
    "privacy": "src/app/privacy/page.tsx",
    "terms": "src/app/terms/page.tsx",
    "refund": "src/app/refund-policy/page.tsx",
    "contact": "src/app/contact/page.tsx",
}

REQUIRED_PUBLIC_ENV = [
    "NEXT_PUBLIC_LEGAL_BUSINESS_NAME",
    "NEXT_PUBLIC_SUPPORT_EMAIL",
    "NEXT_PUBLIC_PLAN_PRICE",
    "NEXT_PUBLIC_REFUND_POLICY_TEXT",
]

PLACEHOLDER_PATTERNS = [
    r"\blorem ipsum\b",
    r"\bTODO\b",
    r"example\.com",
    r"your[- ]company",
    r"your[- ]domain",
    r"coming soon",
]

UNVERIFIED_MARKETING_PATTERNS = [
    r"\btrusted by\b",
    r"\b#\s*1\b",
    r"\bguaranteed\b",
    r"\bindustry[- ]leading\b",
    r"\baward[- ]winning\b",
    r"\b\d{2,}[,+]?\s+(users|customers|companies|teams)\b",
]


class WebsiteComplianceGate:
    """Conservative preflight for payment-provider review readiness.

    This does not replace legal review or Lemon Squeezy approval. It blocks
    obvious incomplete/placeholder sites and unverified social-proof claims.
    """

    def review_source(self, release_dir: Path) -> ComplianceReport:
        errors = []
        warnings = []
        checked = []

        for label, relative in REQUIRED_PAGES.items():
            path = release_dir / relative
            if not path.exists():
                errors.append(f"Missing required public page: {label} ({relative})")
                continue
            checked.append(relative)
            text = path.read_text(encoding="utf-8")
            if len(text.strip()) < 180:
                errors.append(f"Public page is too thin for review: {relative}")

        public_text = "\n".join(
            (release_dir / relative).read_text(encoding="utf-8")
            for relative in REQUIRED_PAGES.values()
            if (release_dir / relative).exists()
        )

        for pattern in PLACEHOLDER_PATTERNS:
            if re.search(pattern, public_text, re.I):
                errors.append(f"Placeholder/incomplete website content matched: {pattern}")

        for pattern in UNVERIFIED_MARKETING_PATTERNS:
            if re.search(pattern, public_text, re.I):
                errors.append(
                    "Potentially unverifiable marketing claim found. "
                    f"Remove or substantiate before merchant review: {pattern}"
                )

        if "Lemon Squeezy" not in public_text:
            warnings.append(
                "Legal/billing pages do not mention Lemon Squeezy as the payment provider."
            )

        return ComplianceReport(
            passed=not errors,
            checked_pages=checked,
            errors=errors,
            warnings=warnings,
        )

    def review_runtime(self) -> ComplianceReport:
        errors = []
        warnings = []
        for key in REQUIRED_PUBLIC_ENV:
            value = os.getenv(key, "").strip()
            if not value:
                errors.append(f"Required review-ready website setting is missing: {key}")
            elif any(x in value.lower() for x in ("example.com", "your company", "todo")):
                errors.append(f"Placeholder value is not allowed for {key}")

        if os.getenv("MERCHANT_REVIEW_ATTESTED", "").strip() != "1":
            errors.append(
                "MERCHANT_REVIEW_ATTESTED=1 is required. Set it only after verifying "
                "the business description, product capabilities, pricing and legal pages are truthful."
            )

        return ComplianceReport(
            passed=not errors,
            errors=errors,
            warnings=warnings,
        )
