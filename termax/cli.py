import click
import termax


@click.group()
@click.version_option(version=termax.__version__)
def cli():
    pass
