import json
import logging
import os
import re
from schemas.analysis import AnalystReport
from schemas.product import (
    BuilderManifest,
    DevTask,
    LandingPage,
    PRD,
    ProductPackage,
    ProductPositioning,
    TechnicalSpec,
    ValidationExperiment,
)

log = logging.getLogger(__name__)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:64] or "microsaas-product"


class ProductManagerAgent:
    """Converts BUILD/VALIDATE analyst theses into build-ready product packages."""

    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6-sol")

    def productize(self, report: AnalystReport, use_ai: bool = False) -> ProductPackage:
        if report.recommendation not in {"BUILD", "VALIDATE"}:
            raise ValueError("Only BUILD or VALIDATE reports can be productized.")

        if use_ai and os.getenv("OPENAI_API_KEY"):
            try:
                return self._productize_with_ai(report)
            except Exception as exc:
                log.warning("AI product design failed; using deterministic fallback: %s", exc)
        return self._fallback(report)

    def _productize_with_ai(self, report: AnalystReport) -> ProductPackage:
        from openai import OpenAI

        prompt = f"""
You are the Product Manager of an AI-native MicroSaaS factory.
Turn this analyst report into a minimal product package that a coding agent can implement.

Analyst report:
{json.dumps(report.model_dump(mode="json"), ensure_ascii=False)}

Rules:
- Preserve the target user's actual job-to-be-done.
- MVP means the smallest paid workflow, not a platform.
- BUILD may be READY_FOR_BUILD.
- VALIDATE must be BLOCKED_FOR_VALIDATION and must include measurable landing-page/preorder/interview experiments.
- Avoid speculative integrations unless required for the core workflow.
- Tasks must be independently testable and have acceptance criteria.
- Prefer a simple web stack: Next.js frontend, Python API only when needed, PostgreSQL/Supabase storage.
- Never invent competitor facts or market evidence beyond the analyst report.
"""
        client = OpenAI()
        response = client.responses.create(
            model=self.model,
            input=prompt,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "product_package",
                    "strict": True,
                    "schema": ProductPackage.model_json_schema(),
                }
            },
            store=False,
        )
        return ProductPackage.model_validate_json(response.output_text)

    def _fallback(self, report: AnalystReport) -> ProductPackage:
        slug = slugify(report.opportunity_title)
        product_name = self._product_name(report.opportunity_title)
        readiness = "READY_FOR_BUILD" if report.recommendation == "BUILD" else "BLOCKED_FOR_VALIDATION"

        positioning = ProductPositioning(
            product_name=product_name,
            one_liner=f"Automate {report.job_to_be_done.rstrip('.').lower()} for {report.target_user}.",
            target_user=report.target_user,
            painful_job=report.job_to_be_done,
            unique_value="A focused workflow with faster setup and less operational overhead than broad all-in-one tools.",
        )

        mvp = report.mvp_features[:4] or ["core workflow", "result export", "basic account management"]
        prd = PRD(
            objective=f"Deliver one paid workflow that solves: {report.job_to_be_done}",
            user_story=f"As {report.target_user}, I want the painful recurring job automated so I can get the result with minimal manual work.",
            in_scope=mvp,
            out_of_scope=[
                "native mobile apps",
                "enterprise SSO and complex roles",
                "marketplace/plugin ecosystem",
                "advanced analytics unrelated to activation or payment",
            ],
            success_metrics=[
                "first-value time under 5 minutes",
                "at least one core workflow completed by a new user",
                "validation conversion meets experiment threshold before expanding scope",
            ],
            acceptance_criteria=[
                "new user can complete the core workflow end-to-end",
                "errors are visible and recoverable",
                "usage can be measured for activation and conversion",
                "pricing/plan limits can be enforced",
            ],
        )

        landing = LandingPage(
            headline=f"Stop doing {self._short_job(report.job_to_be_done)} manually.",
            subheadline=f"{product_name} gives {report.target_user} a focused way to complete the job faster without another bloated platform.",
            problem_bullets=[
                "repetitive manual steps consume time",
                "existing workflows are fragmented or overbuilt",
                "results are hard to repeat consistently",
            ],
            solution_bullets=mvp[:3],
            primary_cta="Start early access",
            pricing_anchor=f"Early access target: USD {report.pricing_low_usd:.0f}-{report.pricing_high_usd:.0f}/month",
            faq=[
                "Who is this for?",
                "What does the MVP automate?",
                "What data or integrations are required?",
                "Can I cancel during early access?",
            ],
        )

        experiments = [
            ValidationExperiment(
                hypothesis="Target users will exchange contact information for early access to this exact workflow.",
                audience=report.target_user,
                channel=(report.acquisition_channels[0] if report.acquisition_channels else "problem-keyword communities"),
                offer=landing.primary_cta,
                primary_metric="qualified visitor-to-waitlist conversion",
                pass_threshold=">= 8% across at least 100 qualified visitors",
                fail_threshold="< 3% across at least 100 qualified visitors",
                max_days=14,
            ),
            ValidationExperiment(
                hypothesis="At least a subset of qualified users will demonstrate willingness to pay before full build.",
                audience=report.target_user,
                channel="direct outreach to users matching the evidence pattern",
                offer=f"Founding plan reservation at USD {report.pricing_low_usd:.0f}/month",
                primary_metric="qualified conversations producing preorder or explicit payment commitment",
                pass_threshold=">= 3 payment commitments from 15 qualified conversations",
                fail_threshold="0 payment commitments from 15 qualified conversations",
                max_days=14,
            ),
        ]

        technical = TechnicalSpec(
            architecture="Single-tenant-feel multi-tenant SaaS with a thin web UI, API layer, background job boundary only if the core workflow is asynchronous.",
            frontend="Next.js + TypeScript",
            backend="Next.js server actions/API routes; add Python/FastAPI only for Python-specific AI/data workloads",
            database="PostgreSQL via Supabase",
            integrations=["Stripe billing", "email provider", "core workflow provider/API only when required"],
            entities=["User", "Workspace", "Job", "Result", "Plan", "UsageEvent"],
            endpoints=[
                "POST /api/jobs",
                "GET /api/jobs/:id",
                "GET /api/results/:id",
                "GET /api/usage",
                "POST /api/billing/checkout",
                "POST /api/billing/webhook",
            ],
            non_functional_requirements=[
                "secrets only in environment variables",
                "basic rate limiting",
                "structured application logs",
                "idempotent billing webhook handling",
                "user data deletion path",
                "core workflow instrumented for activation metrics",
            ],
        )

        tasks = self._tasks(mvp)
        manifest = BuilderManifest(
            product_slug=slug,
            status=readiness,
            source_recommendation=report.recommendation,
            build_goal=f"Ship the smallest testable paid workflow for {report.job_to_be_done}",
            tasks=tasks,
            required_env=["DATABASE_URL", "NEXT_PUBLIC_APP_URL", "STRIPE_SECRET_KEY", "STRIPE_PRICE_ID", "STRIPE_WEBHOOK_SECRET"],
        )

        return ProductPackage(
            source_opportunity=report.opportunity_title,
            source_analyst_score=report.analyst_score,
            readiness=readiness,
            positioning=positioning,
            prd=prd,
            landing_page=landing,
            validation_experiments=experiments,
            pricing_plan=f"Start with one paid tier in the USD {report.pricing_low_usd:.0f}-{report.pricing_high_usd:.0f}/month range plus a constrained trial/early-access path.",
            technical_spec=technical,
            builder_manifest=manifest,
            risks=report.risks,
        )

    @staticmethod
    def _product_name(title: str) -> str:
        words = re.findall(r"[A-Za-z0-9]+", title)
        return "".join(x.capitalize() for x in words[:3])[:28] or "MicroSaaS"

    @staticmethod
    def _short_job(job: str) -> str:
        return " ".join(job.rstrip(".").split()[:7]).lower()

    @staticmethod
    def _tasks(mvp: list[str]) -> list[DevTask]:
        tasks = [
            DevTask(
                id="T001", title="Project foundation",
                description="Create app shell, environment validation, database schema and CI baseline.",
                priority="P0",
                acceptance=["application boots locally", "database migration succeeds", "CI runs tests"],
                dependencies=[],
            ),
            DevTask(
                id="T002", title="Authentication and workspace",
                description="Implement sign-in and a minimal workspace/account boundary.",
                priority="P0",
                acceptance=["user can sign in", "user can access only own workspace data"],
                dependencies=["T001"],
            ),
            DevTask(
                id="T003", title="Core workflow",
                description="Implement the primary job creation, processing and result flow for the MVP.",
                priority="P0",
                acceptance=[f"supports MVP capability: {x}" for x in mvp[:3]],
                dependencies=["T001", "T002"],
            ),
            DevTask(
                id="T004", title="Usage and billing",
                description="Add one paid plan, checkout, webhook processing and usage enforcement.",
                priority="P0",
                acceptance=["checkout creates subscription", "webhook is idempotent", "plan limits are enforced"],
                dependencies=["T001", "T002"],
            ),
            DevTask(
                id="T005", title="Landing and activation instrumentation",
                description="Implement landing page CTA plus activation/conversion events.",
                priority="P1",
                acceptance=["CTA is measurable", "core activation event is logged", "conversion funnel can be inspected"],
                dependencies=["T001"],
            ),
            DevTask(
                id="T006", title="QA and launch readiness",
                description="Cover happy path, failure recovery, secrets, rate limits and deployment checklist.",
                priority="P1",
                acceptance=["critical flow tests pass", "no secrets committed", "production env checklist exists"],
                dependencies=["T003", "T004", "T005"],
            ),
        ]
        return tasks
