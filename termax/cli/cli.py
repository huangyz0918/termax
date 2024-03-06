import click
import inquirer

import termax
from termax.utils import Config, CONFIG_LLM_LIST


@click.group()
@click.version_option(version=termax.__version__)
def cli():
    pass


@cli.command()
def config():
    """
    Set up the global configuration for Termax.
    """
    questions = [
        inquirer.List(
            "platform",
            message="What LLM (platform) are you using?",
            choices=CONFIG_LLM_LIST,
        ),
    ]

    answers = inquirer.prompt(questions)
    click.echo(answers)

    sub_answers = None
    if answers["platform"] == "OpenAI":
        sub_questions = [
            inquirer.Text(
                "api_key",
                message="What is your OpenAI API key?",
            )
        ]
        sub_answers = inquirer.prompt(sub_questions)

    platform = answers["platform"].lower()
    default_config = {
        "model": "gpt-3.5-turbo",
        "platform": platform,
        "api_key": sub_answers["api_key"] if sub_answers else None,
        'temperature': 0.7,
        'save': False,
        'auto_execute': False
    }

    configuration = Config()
    configuration.write_platform(default_config, platform=platform)
    click.echo(configuration.read())
