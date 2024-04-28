import click
from rich.console import Console

import termax
from .utils import *
from termax.utils.const import *
from termax.prompt import Prompt, Memory
from termax.plugin import install_plugin, uninstall_plugin
from termax.utils import Config, CONFIG_PATH, qa_confirm, qa_action, qa_prompt, qa_revise

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
    if not configuration.config.has_section(CONFIG_SEC_GENERAL):
        click.echo(f"General section not found. Running config setup...")
        build_config(general=True)
        config_dict = configuration.read()

    platform = config_dict['general']['platform']
    if not configuration.config.has_section(platform):
        click.echo(f"Platform {platform} section not found. Running config setup...")
        build_config()
        config_dict = configuration.read()

    model, platform = load_model()
    # generate the commands from the model, and execute if auto_execute is True
    intent = qa_prompt()
    if intent is None:
        return

    with console.status(f"[cyan]Guessing..."):
        primary, description = intent['primary'], intent['description']
        guess_prompt = prompt.gen_suggestions(primary, platform)
        command = model.to_command(prompt=guess_prompt, text=description)

    click.echo(f"\nSuggestion:\n")
    console.log(f"{command}\n", style="purple") if command else console.log(
        "Suggestion not readily available. Please revise for better results.\n", style="purple")
    try:
        choice = qa_action() if command else 3
        while True:
            if choice == 0:
                copy_success = copy_command(command)
                print("Command copied to clipboard.") if copy_success else print("Failed to copy the command.")
                break
            elif choice == 1:
                with console.status(f"[cyan]Generating..."):
                    description = model.to_description(prompt.explain_commands(), command)
                console.log(f"{description}")
                break
            elif choice == 2:
                command_success = execute_command(command)
                break
            elif choice == 3:
                description += f" Revised Command: {qa_revise()}"
                command = model.to_command(prompt=guess_prompt, text=description)
                click.echo()
                console.log(f"{command}\n", style="purple")
            else:
                return
            choice = qa_action()
    except KeyboardInterrupt:
        command_success = True
    finally:
        if choice == 2 and command_success:
            save_command(command, description, config_dict, memory)


@cli.command(default_command=True)
@click.argument('text', nargs=-1)
@click.option('--print_cmd', '-p', is_flag=True, help="Print the generated command only.")
def generate(text, print_cmd=False):
    """
    This function will call and generate the commands from LLM
    Args:
        text: the text to be converted into a command.
        print_cmd: if True, only print the generated command.
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
    if not configuration.config.has_section(CONFIG_SEC_GENERAL):
        click.echo(f"General section not found. Running config setup...")
        build_config(general=True)
        config_dict = configuration.read()

    platform = config_dict['general']['platform']
    if not configuration.config.has_section(platform):
        click.echo(f"Platform {platform} section not found. Running config setup...")
        build_config()
        config_dict = configuration.read()

    # load the LLM model
    model, platform = load_model()
    # generate the commands from the model, and execute if auto_execute is True
    with console.status(f"[cyan]Generating..."):
        # loop until the generated command is not ''.
        for i in range(3):
            command = model.to_command(prompt.gen_commands(text, platform), text)
            if command == None:
                return
            elif command != '':
                if not command.startswith('t ') and not command.startswith('termax '):
                    break
                else:
                    text = text + ", do not use command t or termax."
            if i == 2:
                console.log("Unable to generate the command, please try again.")
                return

    if print_cmd:
        print(command)
        # TODO: improve the RAG compatibility using the shell plugin.
        # the command generate using the shell plugin will not be saved in the memory.
        # save_command(command, text, config_dict, memory)
    else:
        if config_dict['general']['show_command'] == "True":
            console.log(command, style="purple")

        choice = None
        command_success = False
        try:
            if config_dict['general']['auto_execute'] == "True":
                command_success = execute_command(command)
            else:
                choice = qa_confirm()
                if choice == 0:
                    command_success = execute_command(command)
                elif choice == 2:
                    with console.status(f"[cyan]Generating..."):
                        description = model.to_description(prompt.explain_commands(), command)
                    console.log(f"{description}")
        except KeyboardInterrupt:
            command_success = True
        finally:
            if config_dict['general']['auto_execute'] == "True" or choice == 0:
                if command_success:
                    save_command(command, text, config_dict, memory)


@cli.command()
@click.option('--general', '-g', is_flag=True, help="Set up the general configuration for Termax.")
def config(general):
    """
    Set up the global configuration for Termax.
    """
    build_config(general)


@cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the plugin to install')
def install(name: str):
    """
    Install the plugin.
    Args:
        name: the name of the plugin, should be in the PLUGIN_LIST.
    """
    install_plugin(name)


@cli.command()
@click.option('--name', '-n', type=str, required=True, help='Name of the plugin to uninstall')
def uninstall(name: str):
    """
    Uninstall the plugin.
    Args:
        name: the name of the plugin, should be in the PLUGIN_LIST.
    """
    uninstall_plugin(name)


@cli.command()
@click.option('--clear', '-c', is_flag=True, help="Clear the memory.")
def rag(clear: bool = False):
    """
    Show all the historical commands in the RAG.
    """
    console = Console()
    commands = memory.get()

    if clear:
        memory.delete()
        console.log("Memory cleared successfully.")
        return

    if commands:
        metadatas = commands['metadatas']
        documents = commands['documents']
        idx = commands['ids']

        for i in range(len(idx)):
            console.log(f"""
                User Input: {documents[i]}
                Generated Commands: {metadatas[i]['response']}
                Date: {metadatas[i]['created_at']}\n
                """)
    else:
        console.log("No commands found in the memory.")
