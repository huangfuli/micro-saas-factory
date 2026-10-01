import json
import re
from pathlib import Path
from schemas.product import ProductPackage


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64] or "product"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def write_product_package(package: ProductPackage, root: str = "products") -> Path:
    folder = Path(root) / package.builder_manifest.product_slug
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "product.json").write_text(
        json.dumps(package.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (folder / "builder_manifest.json").write_text(
        json.dumps(package.builder_manifest.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (folder / "PRD.md").write_text(
        f"""# {package.positioning.product_name} — MVP PRD

## Positioning
{package.positioning.one_liner}

**Target user:** {package.positioning.target_user}

**Painful job:** {package.positioning.painful_job}

**Unique value:** {package.positioning.unique_value}

## Objective
{package.prd.objective}

## User story
{package.prd.user_story}

## In scope
{_bullets(package.prd.in_scope)}

## Out of scope
{_bullets(package.prd.out_of_scope)}

## Success metrics
{_bullets(package.prd.success_metrics)}

## Acceptance criteria
{_bullets(package.prd.acceptance_criteria)}
""",
        encoding="utf-8",
    )

    (folder / "LANDING_PAGE.md").write_text(
        f"""# Landing Page

# {package.landing_page.headline}

{package.landing_page.subheadline}

## Problems
{_bullets(package.landing_page.problem_bullets)}

## What it does
{_bullets(package.landing_page.solution_bullets)}

**CTA:** {package.landing_page.primary_cta}

**Pricing anchor:** {package.landing_page.pricing_anchor}

## FAQ
{_bullets(package.landing_page.faq)}
""",
        encoding="utf-8",
    )

    validation_blocks = []
    for i, exp in enumerate(package.validation_experiments, 1):
        validation_blocks.append(
            f"""## Experiment {i}

**Hypothesis:** {exp.hypothesis}

**Audience:** {exp.audience}

**Channel:** {exp.channel}

**Offer:** {exp.offer}

**Primary metric:** {exp.primary_metric}

**Pass:** {exp.pass_threshold}

**Fail:** {exp.fail_threshold}

**Maximum duration:** {exp.max_days} days
"""
        )
    (folder / "VALIDATION.md").write_text(
        "# Validation Plan\n\n" + "\n".join(validation_blocks),
        encoding="utf-8",
    )

    (folder / "TECH_SPEC.md").write_text(
        f"""# Technical MVP Specification

## Architecture
{package.technical_spec.architecture}

## Stack
- Frontend: {package.technical_spec.frontend}
- Backend: {package.technical_spec.backend}
- Database: {package.technical_spec.database}

## Integrations
{_bullets(package.technical_spec.integrations)}

## Entities
{_bullets(package.technical_spec.entities)}

## Endpoints
{_bullets(package.technical_spec.endpoints)}

## Non-functional requirements
{_bullets(package.technical_spec.non_functional_requirements)}
""",
        encoding="utf-8",
    )

    task_blocks = []
    for task in package.builder_manifest.tasks:
        task_blocks.append(
            f"""## {task.id} — {task.title} [{task.priority}]

{task.description}

**Dependencies:** {", ".join(task.dependencies) if task.dependencies else "none"}

**Acceptance**
{_bullets(task.acceptance)}
"""
        )
    (folder / "TASKS.md").write_text(
        f"# Builder Tasks\n\n**Status:** {package.builder_manifest.status}\n\n"
        + "\n".join(task_blocks),
        encoding="utf-8",
    )

    return folder
