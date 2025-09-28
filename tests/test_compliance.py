from evergreen_os_image.compliance import PRDComplianceReport


def test_current_state_reports_remaining_gaps():
    report = PRDComplianceReport.current_state()

    assert report.fully_compliant is False
    missing = report.missing_requirements()
    identifiers = {status.identifier for status in missing}

    assert identifiers == {"chromebook_support"}

    # Each requirement should have explanatory details to help readers
    assert all(status.details for status in missing)


def test_requirement_map_is_deterministic():
    report = PRDComplianceReport.current_state()
    requirement_map = report.requirement_map()

    assert isinstance(requirement_map, tuple)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in requirement_map)

    keys = [identifier for identifier, _ in requirement_map]
    assert keys == [status.identifier for status in report.statuses]


def test_implemented_requirements_list_progress():
    report = PRDComplianceReport.current_state()
    implemented = {status.identifier for status in report.implemented_requirements()}

    assert implemented == {
        "base_image_composition",
        "ci_pipeline",
        "device_agent_integration",
        "enrollment_ui",
        "flatpak_remotes",
        "security_hardening",
        "update_channels",
    }
