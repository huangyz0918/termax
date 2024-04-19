import re
from urllib.parse import urlparse


def extract_code_from_markdown(markdown_text, separator="\n\n"):
    """
    Extracts code blocks from a markdown text.
    :param markdown_text:  the markdown text.
    :param separator: the separator to join the code blocks.
    :return: a list of code blocks.
    """
    code_block_regex = re.compile(r"```(?:[a-zA-Z0-9]+)?\n(.*?)```", re.DOTALL)
    code_blocks = code_block_regex.findall(markdown_text)

    return separator.join(code_blocks)


def extract_shell_commands(output):
    commands_start = "Commands: "
    commands_index = output.find(commands_start)

    command_start = "Command: "
    command_index = output.find(command_start)

    if command_index >= 0:
        commands = output[command_index + len(command_start):].strip()
    elif commands_index >= 0:
        commands = output[commands_index + len(commands_start):].strip()
    else:
        commands = extract_code_from_markdown(output)

    return commands


def process_mac_script(text):
    """
    Process a script string to remove "osascript -e" and extra quotes,
    then ensure it's wrapped within a single pair of single quotes.

    Args:
    - text (str): The input text potentially containing "osascript -e" and multiple quotes.

    Returns:
    - str: The processed text wrapped within single quotes.
    """
    processed_text = re.sub(r'^\s*osascript -e\s*', '', text)
    if (processed_text.startswith('"') and processed_text.endswith('"')) or (processed_text.startswith("'") and processed_text.endswith("'")):
        processed_text = remove_quotes(processed_text)
    return f"'{processed_text}'"


def process_powershell_script(text):
    """
    Process a PowerShell script string to remove extra quotes and ensure it's wrapped within a single pair of double quotes.

    Args:
    - text (str): The input text potentially containing multiple quotes.

    Returns:
    - str: The processed text wrapped within double quotes.
    """
    processed_text = re.sub(r'^\s*powershell -Command\s*', '', text)
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        processed_text = remove_quotes(text)
    else:
        processed_text = text
    return f'"{processed_text}"'


def remove_quotes(input_string):
    """
    Remove all single and double quotes from the beginning and end of the input string.

    Args:
    - input_string (str): The string from which to remove leading and trailing quotes.

    Returns:
    - str: The modified string with leading and trailing quotes removed.
    """
    # Use a regular expression to remove leading and trailing quotes
    # The pattern looks for quotes at the start (^["']+) and end (["']+$) of the string and removes them
    modified_string = re.sub(r'^["\']+|["\']+$', '', input_string)
    return modified_string


def is_url(string):
    """
    Check if a string is a valid URL.

    Args:
    - string (str): The string to check.

    Returns:
    - bool: True if the string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(string)
        # Check if the parsing succeeded and scheme and netloc are present
        return all([result.scheme, result.netloc])
    except ValueError:
        return False