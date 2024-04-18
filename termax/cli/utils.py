import os
import platform
import subprocess

from termax.prompt import Memory
from termax.agent import OpenAIModel, OllamaModel, GeminiModel, ClaudeModel, QianFanModel, MistralModel, QianWenModel
from termax.utils import Config, qa_general, qa_platform
from termax.utils.const import *


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


def load_model():
    """
    load_model: load the model based on the configuration.
    """
    configuration = Config()
    config_dict = configuration.read()
    plat = config_dict['general']['platform']

    if plat == CONFIG_SEC_OPENAI:
        model = OpenAIModel(
            api_key=config_dict['openai'][CONFIG_SEC_API_KEY], version=config_dict['openai']['model'],
            temperature=float(config_dict['openai']['temperature']), base_url=config_dict['openai']['base_url']
        )
    elif plat == CONFIG_SEC_OLLAMA:
        model = OllamaModel(
            host_url=config_dict['ollama']['host_url'], version=config_dict['ollama']['model'],
        )
    elif plat == CONFIG_SEC_GEMINI:
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
    elif plat == CONFIG_SEC_CLAUDE:
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
    elif plat == CONFIG_SEC_QIANFAN:
        model = QianFanModel(
            api_key=config_dict['qianfan'][CONFIG_SEC_API_KEY], secret_key=config_dict['qianfan']['secret_key'],
            version=config_dict['qianfan']['model'],
            generation_config={
                'temperature': config_dict['qianfan']['temperature'],
                'top_p': config_dict['qianfan']['top_p'],
                'max_output_tokens': config_dict['qianfan']['max_tokens']
            }
        )
    elif plat == CONFIG_SEC_MISTRAL:
        model = MistralModel(
            api_key=config_dict['mistral'][CONFIG_SEC_API_KEY], version=config_dict['mistral']['model'],
            generation_config={
                'temperature': config_dict['mistral']['temperature'],
                'top_p': config_dict['mistral']['top_p'],
                'max_tokens': config_dict['mistral']['max_tokens']
            }
        )
    elif plat == CONFIG_SEC_QIANWEN:
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
        raise ValueError(f"Platform {plat} not supported.")

    return model, plat


def execute_command(command: str) -> bool:
    """
    Execute a command and return whether it was successful.

    Args:
        command: The command to execute.

    Returns:
        True if the command succeeded, False otherwise.
    """
    try:
        if platform.system() == "Windows":
            is_powershell = len(os.getenv("PSModulePath", "").split(os.pathsep)) >= 3
            if is_powershell:
                # Powershell execution
                completed = subprocess.run(['powershell.exe', '-Command', command], check=True)
            else:
                # CMD execution
                completed = subprocess.run(['cmd.exe', '/c', command], check=True)
        else:
            # Unix-like shell execution
            shell = os.environ.get("SHELL", "/bin/sh")
            completed = subprocess.run([shell, '-c', command], check=True)

        return completed.returncode == 0
    except subprocess.CalledProcessError:
        # The command failed
        return False


def save_command(command: str, text: str, config_dict: dict, memory: Memory):
    """
    save_command: save the command into database.
    Args:
        command: the command to execute.
        text: the user prompt.
        config_dict: config dictionary
        memory: vector database in memory
    """
    # add the query to the memory, eviction with the default max size of 2000.
    if config_dict.get(CONFIG_SEC_GENERAL).get('storage_size') is None:
        storage_size = 2000
    else:
        storage_size = int(config_dict[CONFIG_SEC_GENERAL]['storage_size'])

    if memory.count() > storage_size:
        memory.delete()

    if command != '':
        memory.add_query(queries=[{"query": text, "response": command}])


def filter_and_format_history(command_history, filter_condition, max_count):
    """Filter and format command history based on a condition and maximum count."""
    filtered_history = [f"Command: {entry['command']}\nExecution Date: {entry['time']}\n" for entry in
                        command_history if filter_condition(entry)][:max_count]

    return "Command History: \n" + "\n".join(filtered_history)
