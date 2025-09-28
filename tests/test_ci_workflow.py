from evergreen_os_image.ci import GitHubWorkflow


def test_workflow_loads_expected_jobs():
    workflow = GitHubWorkflow.load_default()

    assert workflow.name == "EvergreenOS Build"
    assert set(workflow.jobs) == {"build-artifacts", "smoke-test"}

    build_job = workflow.jobs["build-artifacts"]
    step_names = [step.name for step in build_job.steps]

    assert step_names == [
        "Checkout",
        "Set up Python",
        "Install build tooling",
        "Compose rpm-ostree image",
        "Generate installer ISO",
        "Package QEMU test image",
        "Upload build artifacts",
    ]


def test_workflow_meets_prd_expectations():
    workflow = GitHubWorkflow.load_default()

    assert workflow.meets_prd_expectations is True
