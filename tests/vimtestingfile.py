import cmd
from rich.console import Console
from rich.panel import Panel
from datetime import datetime
from .scraping import Crawler, ContentExtractor
from .preprocessing import ContentWriter
import asyncio


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
            title="[yellow]CurioStack DEBUG CLI[/yellow]",
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
        "Do Nothing Eat something"
        pass

    def do_crawl(self, arg):
        "Start crawl"
        crawl = Crawler(arg)
        asyncio.run(crawl.start())

    def do_extract(self, arg):
        "Start extract"
        extracter = ContentExtractor(arg, limit=5)
        asyncio.run(extracter.start())

    def do_write(self, arg):
        "Start writing"
        writer = ContentWriter(arg, limit=2)
        writer.start()

    def do_status(self, arg):
        "Check status"
        print("status is alive!")

    def do_exit(self, arg):
        "Exit the interpreter"
        print("Goodbye!")
        return True

    def do_clear(self, arg):
        "Clear the command line"
        console.clear()


if __name__ == "__main__":
    CShell().cmdloop()

