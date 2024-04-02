import re


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
