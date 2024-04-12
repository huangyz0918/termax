import os
from pathlib import Path
from rich.console import Console

from termax.utils.const import *


def uninstall_zsh():
    """
    Uninstall the ZSH plugin.
    """
    console = Console()
    with console.status("[cyan]Uninstalling Zsh plugin: ..."):
        try:
            home_path = str(Path.home())
            zshrc_path = os.path.join(home_path, ".zshrc")

            # Read the current contents of the file
            with open(zshrc_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Filter out the plugin
            new_lines = []
            skip = False
            for line in lines:
                if line.strip() == "# ===== Termax ZSH Plugin =====":
                    skip = True
                elif line.strip() == "# ===== Termax ZSH Plugin End =====":
                    skip = False
                    continue
                if not skip:
                    new_lines.append(line)

            # Write the modified contents back to the file
            with open(zshrc_path, "w", encoding="utf-8") as file:
                file.writelines(new_lines)

        except Exception as e:
            console.log(f"Failed to uninstall ZSH plugin: {e}", style="red")
            return

        console.log("Zsh plugin uninstalled successfully.", style="green")


def uninstall_bash():
    """
    Uninstall the Bash plugin.
    """
    console = Console()
    with console.status("[cyan]Uninstalling Bash plugin: ..."):
        try:
            home_path = str(Path.home())
            bashrc_path = os.path.join(home_path, ".bashrc")

            # Read the current contents of the file
            with open(bashrc_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            # Filter out the plugin
            new_lines = []
            skip = False
            for line in lines:
                if line.strip() == "# ====== Termax Bash Plugin ======":
                    skip = True
                elif line.strip() == "# ====== Termax Bash Plugin End ======":
                    skip = False
                    continue
                if not skip:
                    new_lines.append(line)

            # Write the modified contents back to the file
            with open(bashrc_path, "w", encoding="utf-8") as file:
                file.writelines(new_lines)

        except Exception as e:
            console.log(f"Failed to uninstall Bash plugin: {e}", style="red")
            return

        console.log("Bash plugin uninstalled successfully.", style="green")


def uninstall_plugin(plugin_name: str):
    """
    Uninstall the plugin.
    Args:
        plugin_name: the name of the plugin, should be in the PLUGIN_LIST.
    """
    if plugin_name not in PLUGIN_LIST:
        raise ValueError(f"Invalid plugin name: {plugin_name}")

    if plugin_name == PLUGIN_SHELL_ZSH:
        uninstall_zsh()
    elif plugin_name == PLUGIN_SHELL_BASH:
        uninstall_bash()
    else:
        raise ValueError(f"Plugin {plugin_name} is not supported.")
