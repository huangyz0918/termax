import os
import click
import inquirer
import subprocess
from rich.console import Console

import termax
from termax.utils.const import *
from termax.prompt import Prompt
from termax.utils import Config, CONFIG_PATH
from termax.agent import OpenAIModel, GeminiModel, ClaudeModel, QianFanModel, MistralModel, QianWenModel


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
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            # command did not parse, assume it is the default command
            args.insert(0, self.default_command)
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)


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
    selected_platform = answers["platform"].lower()
    general_config = {
        "platform": selected_platform,
        "auto_execute": True,
        "show_command": False
    }

    # configure the platform specific configurations
    sub_answers = None
    if selected_platform == CONFIG_SEC_OPENAI:
        sub_questions = [
            inquirer.Text(
                "api_key",
                message="What is your OpenAI API key?",
            )
        ]
        sub_answers = inquirer.prompt(sub_questions)

    default_config = {}
    platform = selected_platform
    if platform == CONFIG_SEC_OPENAI:
        default_config = {
            "model": "gpt-3.5-turbo",
            "platform": platform,
            "api_key": sub_answers["api_key"] if sub_answers else None,
            'temperature': 0.7,
            'save': False,
            'auto_execute': False
        }

    # configure the auto_execute and show_command for the selected platform
    exe_questions = [
        inquirer.Confirm(
            "auto_execute",
            message="Do you want to execute the generated command automatically?",
            default=True,
        ),
        inquirer.Confirm(
            "show_command",
            message="Do you want to show the generated command?",
            default=False,
        )
    ]
    sub_answers = inquirer.prompt(exe_questions)
    general_config["auto_execute"] = sub_answers["auto_execute"]
    general_config["show_command"] = sub_answers["show_command"]

    # write the configuration to the file
    configuration = Config()
    configuration.write_platform(default_config, platform=platform)
    configuration.write_general(general_config)


@click.group(cls=DefaultCommandGroup)
@click.version_option(version=termax.__version__)
def cli():
    pass


@cli.command(default_command=True)
@click.argument('text', nargs=-1)
def generate(text):
    """
    This function will call and generate the commands from LLM
    """
    console = Console()
    text = " ".join(text)
    configuration = Config()
    # check the configuration available or not
    if not os.path.exists(CONFIG_PATH):
        click.echo("Config file not found. Running config setup...")
        build_config()

    config_dict = configuration.read()
    platform = config_dict['general']['platform']
    if platform == CONFIG_SEC_OPENAI:
        model = OpenAIModel(
            api_key=config_dict['openai']['api_key'], version=config_dict['openai']['model'],
            temperature=float(config_dict['openai']['temperature']),
            prompt=Prompt().nl2commands()
        )
    elif platform == CONFIG_SEC_GEMINI:
        model = GeminiModel(
            api_key=config_dict['gemini']['api_key'], version=config_dict['gemini']['model'],
            generation_config={
                'stop_sequences': config_dict['gemini']['stop_sequences'],
                'temperature': config_dict['gemini']['temperature'],
                'top_p': config_dict['gemini']['top_p'],
                'top_k': config_dict['gemini']['top_k'],
                'candidate_count': config_dict['gemini']['candidate_count'],
                'max_output_tokens': config_dict['gemini']['max_output_tokens']
            },
            prompt=Prompt().nl2commands()
        )
    elif platform == CONFIG_SEC_CLAUDE:
        model = ClaudeModel(
            api_key=config_dict['claude']['api_key'], version=config_dict['claude']['model'],
            generation_config={
                'stop_sequences': config_dict['claude']['stop_sequences'],
                'temperature': config_dict['claude']['temperature'],
                'top_p': config_dict['claude']['top_p'],
                'top_k': config_dict['claude']['top_k'],
                'max_tokens': config_dict['claude']['max_tokens']
            },
            prompt=Prompt().nl2commands()
        )
    elif platform == CONFIG_SEC_QIANFAN:
        model = QianFanModel(
            api_key=config_dict['qianfan']['api_key'], secret_key=config_dict['qianfan']['secret_key'],
            version=config_dict['qianfan']['model'],
            generation_config={
                'temperature': config_dict['qianfan']['temperature'],
                'top_p': config_dict['qianfan']['top_p'],
                'max_output_tokens': config_dict['qianfan']['max_output_tokens']
            },
            prompt=Prompt().nl2commands()
        )
    elif platform == CONFIG_SEC_MISTRAL:
        model = MistralModel(
            api_key=config_dict['mistral']['api_key'], version=config_dict['mistral']['model'],
            generation_config={
                'temperature': config_dict['mistral']['temperature'],
                'top_p': config_dict['mistral']['top_p'],
                'max_tokens': config_dict['mistral']['max_tokens']
            },
            prompt=Prompt().nl2commands()
        )
    elif platform == CONFIG_SEC_QIANWEN:
        model = QianWenModel(
            api_key=config_dict['qianwen']['api_key'], version=config_dict['qianwen']['model'],
            generation_config={
                'temperature': config_dict['qianwen']['temperature'],
                'top_p': config_dict['qianwen']['top_p'],
                'top_k': config_dict['qianwen']['top_k'],
                'stop': config_dict['qianwen']['stop'],
                'max_tokens': config_dict['qianwen']['max_tokens']
            },
            prompt=Prompt().nl2commands()
        )
    else:
        raise ValueError(f"Platform {platform} not supported.")

    # generate the commands from the model, and execute if auto_execute is True
    with console.status(f"[cyan]Generating..."):
        command = model.to_command(text)

    if config_dict['general']['show_command'] == "True":
        click.echo(f"Command: {command}")

    if config_dict['general']['auto_execute']:
        subprocess.run(command, shell=True, text=True)


@cli.command()
def config():
    """
    Set up the global configuration for Termax.
    """
    build_config()
