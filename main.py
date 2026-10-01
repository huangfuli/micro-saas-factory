from rich.console import Console
from rich.table import Table
from orchestrator.workflow import FactoryWorkflow


def main() -> None:
    console = Console()
    results = FactoryWorkflow().run_discovery()
    table = Table(title="MicroSaaS Opportunity Board")
    table.add_column("Decision")
    table.add_column("Score", justify="right")
    table.add_column("Opportunity")
    table.add_column("Target user")
    for item in results:
        table.add_row(item.decision, f"{item.total_score:.2f}", item.title, item.target_user)
    console.print(table)


if __name__ == "__main__":
    main()
