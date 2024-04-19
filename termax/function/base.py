from .openai import MacFunction, ShellFunction, WinFunction

import sys

def get_all_function_schemas():
    """
    Get all function schemas.
    :return: a list of function schemas.
    """
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        return [MacFunction.openai_schema, ShellFunction.openai_schema]
    return [WinFunction.openai_schema, ShellFunction.openai_schema]


def get_all_functions():
    """
    Get all functions.
    :return: a list of functions.
    """
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        return [MacFunction, ShellFunction]  # TODO: load all modules dynamically
    return [WinFunction, ShellFunction] 
