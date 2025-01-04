from typing import Any

import click
from swiftcli import Group

from .commands.clean import CleanCommand
from .version import __version__


def print_version(ctx: click.Context, _: Any, value: bool) -> None:
    if not value:
        return
    msg = "pyproject-cache {}".format(click.style(__version__, fg="yellow"))
    click.echo(msg)
    ctx.exit()


cli = Group(
    params=[
        click.Option(
            ["--version", "-V"],
            is_flag=True,
            callback=print_version,
            help="Display cli version",
        )
    ]
)

cli.add_command_cls(CleanCommand)

if __name__ == "__main__":
    cli()
