import cmd
from rich.console import Console
from rich.panel import Panel
from datetime import datetime

# from curiostack.scraping import Crawler
import threading
import time

console = Console()


def welcome_message():
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    console.print(
        Panel.fit(
            "[bold magenta]Welcome to CurioStack[/bold magenta]\n"
            "[green]Your backend management shell is ready.[/green]\n\n"
            "Type [cyan]help[/cyan] to see available commands.\n"
            "Type [red]exit[/red] to quit.",
            title="[yellow]CurioStack CLI[/yellow]",
            subtitle=f"[cyan]{date}[/cyan] | [cyan]{time}[/cyan]",
            style="bold blue",
        )
    )


class CShell(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.jobs = []

    @property
    def intro(self):
        return welcome_message()

    @property
    def prompt(self):
        # dynamic prompt with colors
        return "\033[1;34m(curiostack)>> \033[0m"

    def emptyline(self):
        """Do nothing when an empty line is entered."""
        pass

    def _scrape_data(self, url):
        """This is the actual function that does the work."""
        print(f"\n[+] Starting scrape for {url}... (This will take 5 seconds)")
        time.sleep(5)  # Simulates a long I/O-bound task like web scraping
        print(f"\n[+] Finished scraping {url}!")

    def do_crawl(self, arg):
        "Start crawl"
        print("crawl is alive!")

    def do_scrape(self, arg):
        "Start scrape"
        # print("content scraping alive!")
        thread = threading.Thread(target=self._scrape_data, args=(arg,))

        thread.daemon = True

        self.jobs.append(thread)

        thread.start()

    def do_write(self, arg):
        "Start writing"
        print("content writing alive!")

    def do_status(self, arg):
        """Check the status of background jobs."""
        if not self.jobs:
            print("No background jobs are running.")
            return
        # Clean up finished jobs from the list before displaying
        self.jobs = [job for job in self.jobs if job.is_alive()]
        print(self.jobs)

        if not self.jobs:
            print("All background jobs have finished.")
            return

        print(f"--- {len(self.jobs)} Active Background Job(s) ---")
        for i, job in enumerate(self.jobs):
            print(f"  Job {i+1}: {'Running' if job.is_alive() else 'Finished'}")

    def do_exit(self, arg):
        "Exit the interpreter"
        print("Goodbye!")
        return True

    def do_clear(self, arg):
        console.clear()


if __name__ == "__main__":
    CShell().cmdloop()

