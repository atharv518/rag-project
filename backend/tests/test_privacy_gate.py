"""
tests/test_privacy_gate.py

Automated tests proving that prohibited data flows are strictly blocked
by the Critical Privacy Gate (External AI Provider Data Handling).
"""

from __future__ import annotations

import pytest

from app.core.config import settings
from app.core.errors import PrivacyPolicyViolationError
from app.core.privacy_gate import DataClassification, PrivacyGateEnforcer


def test_public_and_synthetic_data_allowed_on_free_tier():
    """Public and synthetic test data are allowed on free tier."""
    enforcer = PrivacyGateEnforcer()

    assert enforcer.evaluate_dispatch(
        data_classification=DataClassification.PUBLIC,
        provider_name="gemini",
        model_name="gemini-2.0-flash",
    ) is True

    assert enforcer.evaluate_dispatch(
        data_classification=DataClassification.SYNTHETIC_TEST,
        provider_name="gemini",
        model_name="gemini-2.0-flash",
        is_test_data=True,
    ) is True


def test_organization_confidential_blocked_on_free_tier():
    """Confidential organizational data MUST be blocked from dispatching to free tier."""
    enforcer = PrivacyGateEnforcer()

    with pytest.raises(PrivacyPolicyViolationError) as exc_info:
        enforcer.evaluate_dispatch(
            data_classification=DataClassification.ORGANIZATION_CONFIDENTIAL,
            provider_name="gemini",
            model_name="gemini-2.0-flash",
            organization_id="org-12345",
            is_test_data=False,
        )

    assert "Confidential organizational data requires an approved paid enterprise tier" in str(exc_info.value)
    assert exc_info.value.status_code == 403


def test_personal_sensitive_blocked_on_free_tier():
    """Personal sensitive data / PII MUST be blocked on free tier."""
    enforcer = PrivacyGateEnforcer()

    with pytest.raises(PrivacyPolicyViolationError) as exc_info:
        enforcer.evaluate_dispatch(
            data_classification=DataClassification.PERSONAL_SENSITIVE,
            provider_name="gemini",
            model_name="gemini-2.0-flash",
            is_test_data=False,
        )

    assert exc_info.value.status_code == 403


def test_org_request_without_test_flag_blocked_on_free_tier():
    """Any organization-scoped query without explicit non-confidential test classification is blocked on free tier."""
    enforcer = PrivacyGateEnforcer()

    with pytest.raises(PrivacyPolicyViolationError) as exc_info:
        enforcer.evaluate_dispatch(
            data_classification=DataClassification.PUBLIC,  # even if marked public, org context without test approval blocks
            provider_name="gemini",
            model_name="gemini-2.0-flash",
            organization_id="org-secret-corp",
            is_test_data=False,
        )

    assert "Organization-scoped RAG operations are restricted to approved test data" in str(exc_info.value)

