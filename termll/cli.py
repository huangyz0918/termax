import click
import termll


@click.group()
@click.version_option(version=termll.__version__)
def cli():
    pass
