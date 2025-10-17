import cmd
import asyncio
import argparse
import shlex
import sys
from typing import Optional, List
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm
from pathlib import Path
from .scraping import Crawler, ContentExtractor
from .preprocessing import ContentWriter
from .logger import get_logger
from .config import get_db_path

console = Console()


def format_status(status: str) -> str:
    """Format status with color."""
    status_colors = {
        "running": "[green]Running[/green]",
        "completed": "[blue]Completed[/blue]",
        "failed": "[red]Failed[/red]",
        "pending": "[yellow]Pending[/yellow]",
    }
    return status_colors.get(status.lower(), f"[white]{status}[/white]")


class Job:
    """Represents a background job in the system."""

    def __init__(self, job_id: int, name: str, niche: str, job_type: str):
        self.job_id = job_id
        self.name = name
        self.niche = niche
        self.type = job_type
        self.status = "pending"
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None


def welcome_message():
    """Display a styled welcome message with system status."""
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")

    # Check system status
    db_path = Path(get_db_path("ai_ml"))  # Example niche
    system_status = []

    if db_path.exists():
        system_status.append("[green]Database: Connected[/green]")
    else:
        system_status.append("[red]Database: Not Found[/red]")

    status_text = "\n".join(system_status)

    console.print(
        Panel.fit(
            "[bold magenta]Welcome to CurioStack[/bold magenta]\n"
            "[green]Your backend management shell is ready.[/green]\n\n"
            f"{status_text}\n\n"
            "Type [cyan]help[/cyan] to see available commands.\n"
            "Type [cyan]status[/cyan] to check system status.\n"
            "Type [red]exit[/red] to quit.",
            title="[yellow]CurioStack DEBUG CLI[/yellow]",
            subtitle=f"[cyan]{date}[/cyan] | [cyan]{time}[/cyan]",
            style="bold blue",
        )
    )


class CShell(cmd.Cmd):
    """Enhanced command-line interface for CurioStack."""

    def __init__(self):
        super().__init__()
        self.jobs: List[Job] = []
        self.job_counter = 0
        self.logger = get_logger(__name__, debug=False)

    @property
    def intro(self):
        return welcome_message()

    @property
    def prompt(self):
        return "\033[1;34m(curiostack)>> \033[0m"

    def emptyline(self):
        """Handle empty lines."""
        pass

    def _create_job(self, name: str, niche: str, job_type: str) -> Job:
        """Create a new job and add it to the job list."""
        self.job_counter += 1
        job = Job(self.job_counter, name, niche, job_type)
        self.jobs.append(job)
        return job

    def _update_job_status(self, job: Job, status: str, error: Optional[str] = None):
        """Update job status and handle completion/failure."""
        job.status = status
        if status in ["completed", "failed"]:
            job.end_time = datetime.now()
        if error:
            job.error = error
            self.logger.error(f"Job {job.job_id} failed: {error}")

    def do_crawl(self, args):
        """
        Start crawling process for a specific niche
        Usage: crawl <niche> [--debug]
        """
        parser = argparse.ArgumentParser(description="Start crawling process")
        parser.add_argument("niche", help="Niche to crawl")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")

        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return
        except Exception as e:
            console.print(f"[red]Error parsing arguments: {str(e)}[/red]")
            return

        job = self._create_job("Crawling", parsed.niche, "crawl")
        console.print(
            f"[green]Starting crawl job {job.job_id} "
            f"for niche: {parsed.niche}[/green]"
        )

        try:
            crawl = Crawler(parsed.niche, debug=parsed.debug)
            self._update_job_status(job, "running")
            asyncio.run(crawl.start())
            self._update_job_status(job, "completed")
            console.print(
                f"[green]Crawl job {job.job_id} completed successfully[/green]"
            )
        except Exception as e:
            self._update_job_status(job, "failed", str(e))
            console.print(f"[red]Crawl job {job.job_id} failed: {str(e)}[/red]")

    def do_extract(self, args):
        """
        Extract content from crawled data
        Usage: extract <niche> [--debug] [--limit N]
        """
        parser = argparse.ArgumentParser(description="Start content extraction")
        parser.add_argument("niche", help="Niche to extract content from")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        parser.add_argument(
            "--limit", type=int, default=5, help="Limit the number of items to extract"
        )

        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return
        except Exception as e:
            console.print(f"[red]Error parsing arguments: {str(e)}[/red]")
            return

        if parsed.debug:
            self.logger = get_logger(__name__, debug=True)
            self.logger.info("Debug mode enabled for extraction")

        job = self._create_job("Extraction", parsed.niche, "extract")
        console.print(
            f"[green]Starting extraction job {job.job_id} "
            f"for niche: {parsed.niche}[/green]"
        )

        try:
            extractor = ContentExtractor(
                parsed.niche, limit=parsed.limit, debug=parsed.debug
            )
            self._update_job_status(job, "running")
            asyncio.run(extractor.start())
            self._update_job_status(job, "completed")
            console.print(
                f"[green]Extraction job {job.job_id} completed successfully[/green]"
            )
        except Exception as e:
            self._update_job_status(job, "failed", str(e))
            console.print(f"[red]Extraction job {job.job_id} failed: {str(e)}[/red]")

    def do_write(self, args):
        """
        Write processed content
        Usage: write <niche> [--debug] [--limit N]
        """
        parser = argparse.ArgumentParser(description="Start content writing")
        parser.add_argument("niche", help="Niche to write content for")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        parser.add_argument(
            "--limit", type=int, default=2, help="Limit the number of items to write"
        )

        try:
            parsed = parser.parse_args(shlex.split(args))
        except SystemExit:
            return
        except Exception as e:
            console.print(f"[red]Error parsing arguments: {str(e)}[/red]")
            return

        print(parsed.limit)
        if parsed.debug:
            self.logger = get_logger(__name__, debug=True)
            self.logger.info("Debug mode enabled for writing")

        job = self._create_job("Writing", parsed.niche, "write")
        console.print(
            f"[green]Starting writing job {job.job_id} "
            f"for niche: {parsed.niche}[/green]"
        )

        try:
            writer = ContentWriter(parsed.niche, limit=parsed.limit, debug=parsed.debug)
            self._update_job_status(job, "running")
            if parsed.debug:
                self.logger.info(f"Starting content writing for {parsed.niche}")
            writer.start()
            self._update_job_status(job, "completed")
            msg = f"Writing job {job.job_id} completed successfully"
            console.print(f"[green]{msg}[/green]")
            if parsed.debug:
                self.logger.info(msg)
        except Exception as e:
            self._update_job_status(job, "failed", str(e))
            error_msg = f"Writing job {job.job_id} failed: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            if parsed.debug:
                self.logger.error(error_msg)

    def do_jobs(self, _):
        """Display status of all jobs."""
        if not self.jobs:
            console.print("[yellow]No jobs found[/yellow]")
            return

        table = Table(title="Jobs Status")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Niche", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Start Time", style="cyan")
        table.add_column("Duration", style="green")

        for job in self.jobs:
            duration = (job.end_time or datetime.now()) - job.start_time
            duration_str = str(duration).split(".")[0]  # Remove microseconds

            table.add_row(
                str(job.job_id),
                job.name,
                job.niche,
                job.type,
                format_status(job.status),
                job.start_time.strftime("%H:%M:%S"),
                duration_str,
            )

        console.print(table)

    def do_status(self, _):
        """Display system status and configuration."""
        table = Table(title="System Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="yellow")

        # Check database
        db_path = Path(get_db_path("ai_ml"))
        db_status = (
            "[green]Connected[/green]" if db_path.exists() else "[red]Not Found[/red]"
        )
        table.add_row("Database", db_status)

        # Add active jobs count
        active_jobs = sum(1 for job in self.jobs if job.status == "running")
        table.add_row("Active Jobs", f"[blue]{active_jobs}[/blue]")

        console.print(table)

    def do_clear(self, _):
        """Clear the terminal screen."""
        console.clear()
        self.intro

    def do_exit(self, _):
        """Exit the CLI."""
        if any(job.status == "running" for job in self.jobs):
            confirm_msg = (
                "[yellow]There are running jobs."
                " Are you sure you want to exit?[/yellow]"
            )
            if not Confirm.ask(confirm_msg):
                return False
        console.print("[magenta]Goodbye![/magenta]")
        return True

    def default(self, line):
        """Handle unknown commands."""
        console.print(f"[red]Unknown command: {line}[/red]")
        console.print("Type [cyan]help[/cyan] for a list of commands")


if __name__ == "__main__":
    try:
        CShell().cmdloop()
    except KeyboardInterrupt:
        msg = "[yellow]Received keyboard interrupt. Exiting...[/yellow]"
        console.print(f"\n{msg}")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)
