import argparse
from rich.console import Console
from rich.table import Table
from orchestrator.workflow import FactoryWorkflow


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analyze", action="store_true", help="run Analyst on PASS opportunities")
    parser.add_argument(
        "--web-research",
        action="store_true",
        help="enable OpenAI Responses web_search for current competitor/pricing research",
    )
    parser.add_argument(
        "--productize",
        action="store_true",
        help="convert BUILD/VALIDATE analyst results into product packages",
    )
    parser.add_argument(
        "--pm-ai",
        action="store_true",
        help="use Structured Outputs to enrich product packages; requires OPENAI_API_KEY",
    )
    args = parser.parse_args()

    console = Console()
    workflow = FactoryWorkflow()
    results, scout_report = workflow.run_discovery()
    show_scout(console, results)
    console.print(f"\nScout report: {scout_report}")

    should_analyze = args.analyze or args.web_research or args.productize or args.pm_ai
    if should_analyze:
        reports, analyst_report = workflow.run_analysis(results, web_research=args.web_research)
        console.print()
        show_analyst(console, reports)
        console.print(f"\nAnalyst report: {analyst_report}")

        if args.productize or args.pm_ai:
            outputs = workflow.run_productization(reports, use_ai=args.pm_ai)
            console.print()
            show_products(console, outputs)
            if outputs:
                console.print("\nBuild-ready products are appended to data/build_queue.jsonl.")
            else:
                console.print("\nNo BUILD/VALIDATE thesis qualified for productization.")


if __name__ == "__main__":
    main()
