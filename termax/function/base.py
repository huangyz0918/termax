from .macos import MacFunction


def get_all_function_schemas():
    """
    Get all function schemas.
    :return: a list of function schemas.
    """
    return [MacFunction.openai_schema]


def get_all_functions():
    """
    Get all functions.
    :return: a list of functions.
    """
    return [MacFunction]  # TODO: load all modules dynamically
