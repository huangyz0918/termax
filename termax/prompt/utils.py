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
    command_start = "Commands: "
    start_index = output.find(command_start)

    if start_index == -1:
        commands = extract_code_from_markdown(output)
    else:
        commands = output[start_index + len(command_start):].strip()

    return commands
