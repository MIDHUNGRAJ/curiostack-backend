# import typer


# def main(name: str):
#     print(f"Hello {name}")


# if __name__ == "__main__":
#     typer.run(main)

# import typer

# app = typer.Typer()


# @app.command()
# def hello(name: str = "monee"):
#     print(f"Hello {name}")


# @app.command()
# def goodbye(name: str, formal: bool = False):
#     if formal:
#         print(f"Goodbye Ms. {name}. Have a good day.")
#     else:
#         print(f"Bye {name}!")


# if __name__ == "__main__":
#     app()

import cmd
from rich.console import Console

console = Console()


class CShell(cmd.Cmd):

    @property
    def intro(self):
        return "WELCOME TO CURIOSTACK"

    @property
    def prompt(self):
        # dynamic prompt with colors
        return "\033[1;32m(curiostack)> \033[0m"

    def do_greet(self, arg):
        'Greet the user: greet [name]'
        if arg:
            print(f"Hello, {arg}!")
        else:
            print("Hello!")

    def do_quit(self, arg):
        'Exit the interpreter'
        print('Goodbye!')
        return True


if __name__ == '__main__':
    CShell().cmdloop()
