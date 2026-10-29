"""
app/core/privacy_gate.py

Technical enforcement for External AI Provider Data Handling (Critical Privacy Gate).

Enforces data classification rules:
- Unpaid/free-tier providers (such as Gemini Free Tier) are permitted ONLY for
  synthetic, public, or explicitly approved non-confidential test data.
- Organization-scoped confidential data or PII is strictly prohibited from being
  routed to unpaid providers where external training or human review may occur.
- No silent fallback from approved paid provider to unpaid tier.
- Policy evaluation decisions are logged in structured format with data classification,
  provider, model, and decision, without logging raw document text or PII.
"""

from __future__ import annotations

import enum
from typing import Any

import structlog

from app.core.config import settings
from app.core.errors import PrivacyPolicyViolationError

log = structlog.get_logger(__name__)


class DataClassification(str, enum.Enum):
    """Classification of data sensitivity."""
    PUBLIC = "public"
    SYNTHETIC_TEST = "synthetic_test"
    NON_CONFIDENTIAL_TEST = "non_confidential_test"
    PERSONAL_SENSITIVE = "personal_sensitive"
    ORGANIZATION_CONFIDENTIAL = "organization_confidential"
    RESTRICTED = "restricted"


class AIProviderTier(str, enum.Enum):
    """External provider subscription/privacy tier."""
    FREE = "free"  # Unpaid: inputs/outputs may be retained/used for model training and human review
    PAID = "paid"  # Paid / Enterprise: non-training guarantees and privacy SLA enforced


class PrivacyGateEnforcer:
    """Enforces data-sensitivity routing rules before any external AI provider dispatch."""

    @staticmethod
    def evaluate_dispatch(
        *,
        data_classification: DataClassification | str,
        provider_name: str,
        model_name: str,
        organization_id: str | None = None,
        is_test_data: bool = False,
    ) -> bool:
        """Evaluate whether a request can be routed to the external provider.

        Raises:
            PrivacyPolicyViolationError: If routing violates the privacy gate.
        """
        classification = (
            data_classification
            if isinstance(data_classification, DataClassification)
            else DataClassification(data_classification)
        )

        active_tier = AIProviderTier(settings.EXTERNAL_AI_DATA_TIER.lower())

        # Rule 1: Organization confidential data cannot go to Free Tier unless explicit override
        if classification in (
            DataClassification.ORGANIZATION_CONFIDENTIAL,
            DataClassification.RESTRICTED,
            DataClassification.PERSONAL_SENSITIVE,
        ):
            if active_tier == AIProviderTier.FREE:
                if not (settings.ALLOW_ORG_DATA_ON_FREE_TIER and is_test_data):
                    log.error(
                        "privacy_gate_blocked",
                        reason="Confidential/sensitive data cannot be sent to external AI provider on free tier",
                        data_classification=classification.value,
                        provider=provider_name,
                        model=model_name,
                        tier=active_tier.value,
                        organization_id=organization_id,
                    )
                    raise PrivacyPolicyViolationError(
                        f"Data classification '{classification.value}' cannot be sent to provider "
                        f"'{provider_name}' on the '{active_tier.value}' tier. "
                        "Confidential organizational data requires an approved paid enterprise tier."
                    )

        # Rule 2: If organization_id is present and tier is free, enforce that data must be non-confidential test data
        if organization_id and active_tier == AIProviderTier.FREE and not is_test_data:
            log.warn(
                "privacy_gate_org_on_free_tier_warning",
                organization_id=organization_id,
                provider=provider_name,
                model=model_name,
                data_classification=classification.value,
            )
            if not settings.ALLOW_ORG_DATA_ON_FREE_TIER:
                raise PrivacyPolicyViolationError(
                    f"Organization-scoped RAG operations are restricted to approved test data "
                    f"under the current free-tier configuration."
                )

        # Approved dispatch
        log.info(
            "privacy_gate_approved",
            data_classification=classification.value,
            provider=provider_name,
            model=model_name,
            tier=active_tier.value,
            organization_id=organization_id,
            is_test_data=is_test_data,
        )
        return True


privacy_gate = PrivacyGateEnforcer()

