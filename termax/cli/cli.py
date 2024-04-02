import os
import click
import subprocess
from rich.console import Console

import termax
from termax.utils.const import *
from termax.prompt import Prompt, Memory
from termax.utils.metadata import get_command_history
from termax.utils import Config, CONFIG_PATH, qa_general, qa_platform, qa_confirm
from termax.agent import OpenAIModel, GeminiModel, ClaudeModel, QianFanModel, MistralModel, QianWenModel

memory = Memory()
# avoid the tokenizers parallelism issue
os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class DefaultCommandGroup(click.Group):
    """allow a default command for a group"""

    def command(self, *args, **kwargs):
        """
        command: the command decorator for the group.
        """
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
        """
        resolve_command: resolve the command.
        """
        try:
            # test if the command parses
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)
        except click.UsageError:
            # command did not parse, assume it is the default command
            args.insert(0, self.default_command)
            return super(DefaultCommandGroup, self).resolve_command(ctx, args)


def build_config(general: bool = False):
    """
    build_config: build the configuration for Termax.
    Args:
        general: a boolean indicating whether to build the general configuration only.
    :return:
    """
    configuration = Config()
    if general:  # configure the general configurations
        general_config = qa_general()
        if general_config:
            configuration.write_general(general_config)
    else:  # configure the platform configurations
        platform_config = qa_platform()
        if platform_config:
            configuration.write_platform(platform_config, platform=platform_config['platform'])

    if not configuration.config.has_section(CONFIG_SEC_GENERAL):
        click.echo("\nGeneral section not found. Running config setup...")
        general_config = qa_general()
        configuration.write_general(general_config)


def load_model():
    """
    load_model: load the model based on the configuration.
    """
    configuration = Config()
    config_dict = configuration.read()
    platform = config_dict['general']['platform']

    if platform == CONFIG_SEC_OPENAI:
        model = OpenAIModel(
            api_key=config_dict['openai'][CONFIG_SEC_API_KEY], version=config_dict['openai']['model'],
            temperature=float(config_dict['openai']['temperature'])
        )
    elif platform == CONFIG_SEC_GEMINI:
        model = GeminiModel(
            api_key=config_dict['gemini'][CONFIG_SEC_API_KEY], version=config_dict['gemini']['model'],
            generation_config={
                'stop_sequences': config_dict['gemini']['stop_sequences']
                if config_dict['gemini']['stop_sequences'] != 'None' else None,
                'temperature': config_dict['gemini']['temperature'],
                'top_p': config_dict['gemini']['top_p'],
                'top_k': config_dict['gemini']['top_k'],
                'candidate_count': config_dict['gemini']['candidate_count'],
                'max_output_tokens': config_dict['gemini']['max_tokens']
            }
        )
    elif platform == CONFIG_SEC_CLAUDE:
        model = ClaudeModel(
            api_key=config_dict['claude'][CONFIG_SEC_API_KEY], version=config_dict['claude']['model'],
            generation_config={
                'stop_sequences': config_dict['claude']['stop_sequences']
                if config_dict['claude']['stop_sequences'] != 'None' else None,
                'temperature': config_dict['claude']['temperature'],
                'top_p': config_dict['claude']['top_p'],
                'top_k': config_dict['claude']['top_k'],
                'max_tokens': config_dict['claude']['max_tokens']
            }
        )
    elif platform == CONFIG_SEC_QIANFAN:
        model = QianFanModel(
            api_key=config_dict['qianfan'][CONFIG_SEC_API_KEY], secret_key=config_dict['qianfan']['secret_key'],
            version=config_dict['qianfan']['model'],
            generation_config={
                'temperature': config_dict['qianfan']['temperature'],
                'top_p': config_dict['qianfan']['top_p'],
                'max_output_tokens': config_dict['qianfan']['max_tokens']
            }
        )
    elif platform == CONFIG_SEC_MISTRAL:
        model = MistralModel(
            api_key=config_dict['mistral'][CONFIG_SEC_API_KEY], version=config_dict['mistral']['model'],
            generation_config={
                'temperature': config_dict['mistral']['temperature'],
                'top_p': config_dict['mistral']['top_p'],
                'max_tokens': config_dict['mistral']['max_tokens']
            }
        )
    elif platform == CONFIG_SEC_QIANWEN:
        model = QianWenModel(
            api_key=config_dict['qianwen'][CONFIG_SEC_API_KEY], version=config_dict['qianwen']['model'],
            generation_config={
                'temperature': config_dict['qianwen']['temperature'],
                'top_p': config_dict['qianwen']['top_p'],
                'top_k': config_dict['qianwen']['top_k'],
                'stop': config_dict['qianwen']['stop_sequences']
                if config_dict['qianwen']['stop_sequences'] != 'None' else None,
                'max_tokens': config_dict['qianwen']['max_tokens']
            }
        )
    else:
        raise ValueError(f"Platform {platform} not supported.")

    return model


@click.group(cls=DefaultCommandGroup)
@click.version_option(version=termax.__version__)
def cli():
    """
    Termax: A CLI tool to generate and execute commands from natural language.
    """
    pass


@cli.command()
def guess():
    """
    Guess the next command based on the information provided.
    """
    console = Console()
    prompt = Prompt(memory)
    configuration = Config()

    config_dict = configuration.read()
    platform = config_dict['general']['platform']
    if not configuration.config.has_section(platform):
        click.echo(f"Platform {platform} section not found. Running config setup...")
        build_config()
        config_dict = configuration.read()

    model = load_model()
    # generate the commands from the model, and execute if auto_execute is True
    with console.status(f"[cyan]Guessing..."):
        prompt_txt = prompt.gen_suggestions()

        history, index = "Command History: \n", 0
        for i in get_command_history()['shell_command_history']:
            if i['command'] in ("t guess", "termax guess"):
                continue

            history += f"""
            Command: {i['command']}
            Date: {i['time']}\n
            """
            index += 1
            if index >= COMMAND_HISTORY_COUNT:
                break

        command = model.guess_command(history, prompt_txt)

    if config_dict['general']['show_command'] == "True":
        console.log(f"Generated command: {command}")

    if config_dict['general']['auto_execute'] == "True":
        subprocess.run(command, shell=True, text=True)
    else:
        choice = qa_confirm()
        if choice == 0:
            subprocess.run(command, shell=True, text=True)
        elif choice == 2:
            with console.status(f"[cyan]Generating..."):
                description = model.to_description(prompt.explain_commands(), command)
            console.log(f"{description}")


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

    prompt = Prompt(memory)
    config_dict = configuration.read()
    platform = config_dict['general']['platform']
    if not configuration.config.has_section(platform):
        click.echo(f"Platform {platform} section not found. Running config setup...")
        build_config()
        config_dict = configuration.read()

    # load the LLM model
    model = load_model()

    # generate the commands from the model, and execute if auto_execute is True
    with console.status(f"[cyan]Generating..."):
        command = model.to_command(prompt.gen_commands(text), text)

    if config_dict['general']['show_command'] == "True":
        console.log(f"Generated command: {command}")

    def execute_command(cmd: str):
        """
        execute_command: execute the command.
        Args:
            cmd: the command to execute.
        """
        try:
            subprocess.run(cmd, shell=True, text=True)
        except KeyboardInterrupt:
            pass
        finally:
            # add the query to the memory, eviction with the default max size of 2000.
            if config_dict.get(CONFIG_SEC_GENERAL).get('storage_size') is None:
                storage_size = 2000
            else:
                storage_size = int(config_dict[CONFIG_SEC_GENERAL]['storage_size'])

            if memory.count() > storage_size:
                memory.delete()

            if cmd != '':
                memory.add_query(queries=[{"query": text, "response": cmd}])

    if config_dict['general']['auto_execute'] == "True":
        execute_command(command)
    else:
        choice = qa_confirm()
        if choice == 0:
            execute_command(command)
        elif choice == 2:
            with console.status(f"[cyan]Generating..."):
                description = model.to_description(prompt.explain_commands(), command)
            console.log(f"{description}")


@cli.command()
@click.option('--general', '-g', is_flag=True, help="Set up the general configuration for Termax.")
def config(general):
    """
    Set up the global configuration for Termax.
    """
    build_config(general)
