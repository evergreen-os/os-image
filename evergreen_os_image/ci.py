"""Helpers for inspecting EvergreenOS GitHub Actions workflows."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, Tuple

from .configuration import REPO_ROOT


@dataclass(frozen=True)
class WorkflowStep:
    """Single step in a GitHub Actions job."""

    name: str
    uses: str | None
    run: str | None


@dataclass(frozen=True)
class WorkflowJob:
    """Represents a CI job composed of sequential steps."""

    identifier: str
    runs_on: str
    steps: Tuple[WorkflowStep, ...]
    needs: Tuple[str, ...]


@dataclass(frozen=True)
class GitHubWorkflow:
    """Structured view of the EvergreenOS build workflow."""

    name: str
    triggers: Mapping[str, object]
    jobs: Mapping[str, WorkflowJob]

    @classmethod
    def load_default(cls, path: Path | None = None) -> "GitHubWorkflow":
        """Load the default EvergreenOS workflow from disk."""

        workflow_path = path or REPO_ROOT / ".github" / "workflows" / "build.yml"
        data = json.loads(workflow_path.read_text())

        jobs: Dict[str, WorkflowJob] = {}
        for identifier, job_data in data.get("jobs", {}).items():
            raw_needs = job_data.get("needs", ())
            if isinstance(raw_needs, str):
                needs: Tuple[str, ...] = (raw_needs,)
            else:
                needs = tuple(raw_needs)

            steps = tuple(
                WorkflowStep(
                    name=step.get("name", ""),
                    uses=step.get("uses"),
                    run=step.get("run"),
                )
                for step in job_data.get("steps", [])
            )

            jobs[identifier] = WorkflowJob(
                identifier=identifier,
                runs_on=job_data.get("runs-on", ""),
                steps=steps,
                needs=needs,
            )

        return cls(name=data.get("name", ""), triggers=data.get("on", {}), jobs=jobs)

    @property
    def meets_prd_expectations(self) -> bool:
        """Whether the workflow aligns with EvergreenOS build requirements."""

        required_jobs = {"build-artifacts", "smoke-test"}
        if not required_jobs.issubset(self.jobs.keys()):
            return False

        build_job = self.jobs["build-artifacts"]
        step_names = [step.name for step in build_job.steps]
        expected_build_steps = {
            "Checkout",
            "Set up Python",
            "Install build tooling",
            "Compose rpm-ostree image",
            "Generate installer ISO",
            "Package QEMU test image",
            "Upload build artifacts",
        }
        if not expected_build_steps.issubset(step_names):
            return False

        smoke_job = self.jobs["smoke-test"]
        smoke_step_names = {step.name for step in smoke_job.steps}
        expected_smoke_steps = {
            "Checkout",
            "Download build artifacts",
            "Boot QEMU smoke test",
        }
        if not expected_smoke_steps.issubset(smoke_step_names):
            return False

        return True


__all__ = ["WorkflowStep", "WorkflowJob", "GitHubWorkflow"]
