import os
import click
import inquirer

import termax
from termax.utils import Config, CONFIG_LLM_LIST, CONFIG_PATH
from termax.prompt import Prompt
from termax.agent import OpenAIModel


class DefaultCommandGroup(click.Group):
    """allow a default command for a group"""

    def command(self, *args, **kwargs):
        default_command = kwargs.pop('default_command', False)
        if default_command and not args:
            kwargs['name'] = kwargs.get('name', 'termax/t')
        decorator = super(
            DefaultCommandGroup, self).command(*args, **kwargs)

        if default_command:
            def new_decorator(f):
                cmd = decorator(f)
                self.default_command = cmd.name
                return cmd

            return new_decorator

        return decorator

    def resolve_command(self, ctx, args):
        try:
            # test if the command parses
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            # command did not parse, assume it is the default command
            args.insert(0, self.default_command)
            return super(
                DefaultCommandGroup, self).resolve_command(ctx, args)


def build_config():
    """
    build_config: build the configuration for Termax.
    :return:
    """
    questions = [
        inquirer.List(
            "platform",
            message="What LLM (platform) are you using?",
            choices=CONFIG_LLM_LIST,
        ),
    ]

    answers = inquirer.prompt(questions)

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


@click.group(cls=DefaultCommandGroup)
@click.version_option(version=termax.__version__)
def cli():
    pass


@cli.command(default_command=True)
@click.argument('text')
def generate(text):
    """
    This function will call and generate the commands from LLM
    """
    config_dict = Config().read()
    # check the configuration available or not
    if not os.path.exists(CONFIG_PATH):
        click.echo("Config file not found. Running config setup...")
        build_config()

    # Call the openAI API request, the parameter "text" is the input text.
    model = OpenAIModel(
        api_key=config_dict['openai']['api_key'], version=config_dict['openai']['model'],
        temperature=float(config_dict['openai']['temperature']),
        prompt=Prompt().produce(text)
    )
    model.to_command(request=text)


@cli.command()
def config():
    """
    Set up the global configuration for Termax.
    """
    build_config()
