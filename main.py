from rich.console import Console
from rich.table import Table
from orchestrator.workflow import FactoryWorkflow


def main() -> None:
    console = Console()
    results, report_path = FactoryWorkflow().run_discovery()
    table = Table(title="Scout v0.2 — Live MicroSaaS Opportunity Board")
    table.add_column("Decision")
    table.add_column("Score", justify="right")
    table.add_column("Opportunity")
    table.add_column("Evidence", justify="right")
    for item in results:
        table.add_row(item.decision, f"{item.total_score:.2f}", item.title, str(len(item.evidence)))
    console.print(table)
    if report_path:
        console.print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
