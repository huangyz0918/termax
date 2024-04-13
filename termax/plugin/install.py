import os
from pathlib import Path
from rich.console import Console

from .shell import *
from termax.utils.const import *


def install_zsh():
    """
    Install the ZSH plugin.
    """
    console = Console()
    with console.status(f"[cyan]Installing plugin Zsh: ..."):
        try:
            home_path = str(Path.home())
            zshrc_path = os.path.join(home_path, ".zshrc")

            with open(zshrc_path, "a", encoding="utf-8") as file:
                file.write(zsh_plugin)
        except Exception as e:
            console.log(f"Failed to install ZSH plugin: {e}", style="red")
    console.log("Zsh plugin installed successfully.", style="green")


def install_bash():
    """
    Install the Bash plugin.
    """
    console = Console()
    with console.status(f"[cyan]Installing plugin Bash: ..."):
        try:
            home_path = str(Path.home())
            bashrc_path = os.path.join(home_path, ".bashrc")

            with open(bashrc_path, "a", encoding="utf-8") as file:
                file.write(bash_plugin)
        except Exception as e:
            console.log(f"Failed to install Bash plugin: {e}", style="red")
    console.log("Bash plugin installed successfully.", style="green")


def install_fish():
    """
    Install the Fish plugin.
    """
    console = Console()
    with console.status(f"[cyan]Installing plugin Fish: ..."):
        try:
            home_path = str(Path.home())
            fish_plugin_path = os.path.join(home_path, ".config/fish/config.fish")
            fish_function_path = os.path.join(home_path, ".config/fish/functions/termax_fish.fish")

            with open(fish_plugin_path, "a", encoding="utf-8") as file:
                file.write(fish_plugin)
            with open(fish_function_path, "a", encoding="utf-8") as file:
                file.write(fish_function)
            
        except Exception as e:
            console.log(f"Failed to install Fish plugin: {e}", style="red")
    console.log("Fish plugin installed successfully.", style="green")


def install_plugin(plugin_name: str):
    """
    Install the plugin.
    Args:
        plugin_name: the name of the plugin, should be in the PLUGIN_LIST.
    """
    if plugin_name not in PLUGIN_LIST:
        raise ValueError(f"Invalid plugin name: {plugin_name}")

    if plugin_name == PLUGIN_SHELL_ZSH:
        install_zsh()
    elif plugin_name == PLUGIN_SHELL_BASH:
        install_bash()
    elif plugin_name == PLUGIN_SHELL_FISH:
        install_fish()
    else:
        raise ValueError(f"Plugin {plugin_name} is not supported.")
