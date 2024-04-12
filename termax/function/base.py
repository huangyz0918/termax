from termax.function.openai.macos import MacFunction
from termax.function.openai.shell import ShellFunction

def get_all_function_schemas():
    """
    Get all function schemas.
    :return: a list of function schemas.
    """
    return [MacFunction.openai_schema, ShellFunction.openai_schema]


def get_all_functions():
    """
    Get all functions.
    :return: a list of functions.
    """
    return [MacFunction, ShellFunction]  # TODO: load all modules dynamically


def get_function(name: str):
    for function in get_all_functions():
        if function.openai_schema["name"] == name:
            return function
