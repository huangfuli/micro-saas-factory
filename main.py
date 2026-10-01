import argparse
from rich.console import Console
from rich.table import Table
from orchestrator.workflow import FactoryWorkflow
from builder.agent import BuilderAgent


def show_scout(console, results):
    table = Table(title="Scout v0.3 — MicroSaaS Opportunity Board")
    table.add_column("Gate")
    table.add_column("Score", justify="right")
    table.add_column("Commercial", justify="right")
    table.add_column("Evidence", justify="right")
    table.add_column("Opportunity")
    for item in results:
        table.add_row(
            item.decision,
            f"{item.total_score:.2f}",
            f"{item.commercial_intent_score:.1f}",
            str(len(item.evidence)),
            item.title,
        )
    console.print(table)


def show_analyst(console, reports):
    table = Table(title="Analyst v0.1 — Commercial Validation Board")
    table.add_column("Decision")
    table.add_column("Score", justify="right")
    table.add_column("Price")
    table.add_column("Opportunity")
    for report in reports:
        table.add_row(
            report.recommendation,
            f"{report.analyst_score:.1f}",
            f"USD {report.pricing_low_usd:.0f}-{report.pricing_high_usd:.0f}/mo",
            report.opportunity_title,
        )
    console.print(table)


def show_products(console, outputs):
    table = Table(title="Product Manager v0.1 — Productization Board")
    table.add_column("Readiness")
    table.add_column("Builder queue")
    table.add_column("Product")
    table.add_column("Package")
    for output in outputs:
        package = output["package"]
        table.add_row(
            package.readiness,
            "QUEUED" if output["queued"] else "NOT QUEUED",
            package.positioning.product_name,
            output["folder"],
        )
    console.print(table)


def show_build(console, result):
    if result is None:
        console.print("Builder queue is empty.")
        return
    table = Table(title="Builder Agent v0.1 — Build Result")
    table.add_column("Status")
    table.add_column("Product")
    table.add_column("Workspace")
    table.add_column("Files", justify="right")
    table.add_row(
        result.status,
        result.product_slug,
        result.workspace,
        str(len(result.generated_files)),
    )
    console.print(table)
    if result.errors:
        console.print("\nErrors:")
        for error in result.errors:
            console.print(f"- {error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--web-research", action="store_true")
    parser.add_argument("--productize", action="store_true")
    parser.add_argument("--pm-ai", action="store_true")
    parser.add_argument("--build-next", action="store_true", help="consume next Builder queue item")
    parser.add_argument("--builder-ai", action="store_true", help="generate product-specific src/ code")
    parser.add_argument("--install", action="store_true", help="run npm install in generated workspace")
    parser.add_argument("--qa", action="store_true", help="run npm install + lint + build")
    parser.add_argument("--clean-build", action="store_true", help="recreate existing workspace")
    args = parser.parse_args()

    console = Console()

    if args.build_next:
        result = BuilderAgent().build_next(
            use_ai=args.builder_ai,
            install=args.install,
            qa=args.qa,
            clean=args.clean_build,
        )
        show_build(console, result)
        return

    workflow = FactoryWorkflow()
    results, scout_report = workflow.run_discovery()
    show_scout(console, results)
    console.print(f"\nScout report: {scout_report}")

    should_analyze = args.analyze or args.web_research or args.productize or args.pm_ai
    if should_analyze:
        reports, analyst_report = workflow.run_analysis(
            results,
            web_research=args.web_research,
        )
        console.print()
        show_analyst(console, reports)
        console.print(f"\nAnalyst report: {analyst_report}")

        if args.productize or args.pm_ai:
            outputs = workflow.run_productization(reports, use_ai=args.pm_ai)
            console.print()
            show_products(console, outputs)


if __name__ == "__main__":
    main()
