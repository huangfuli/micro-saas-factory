from pathlib import Path

from launch.compliance import REQUIRED_PAGES, WebsiteComplianceGate


def test_compliance_rejects_incomplete_site(tmp_path):
    report = WebsiteComplianceGate().review_source(tmp_path)
    assert report.passed is False
    assert report.errors


def test_compliance_accepts_complete_truthful_site(tmp_path):
    for relative in REQUIRED_PAGES.values():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "A real SaaS product description. " * 12
            + " Payments are processed by Lemon Squeezy.",
            encoding="utf-8",
        )

    report = WebsiteComplianceGate().review_source(tmp_path)
    assert report.passed is True
