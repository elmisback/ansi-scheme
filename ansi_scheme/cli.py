from .user import User
from .ls import ls
from .load import load

import click

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = User()

cli.add_command(ls)
cli.add_command(load)
