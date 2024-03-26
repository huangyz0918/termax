import inquirer
from termax.utils.const import *


def qa_platform(model_list: dict = CONFIG_LLM_LIST):
    """
    qa_platform: ask the user to input the platform related configuration.

    Args:
        model_list: the list of models.
    """
    try:
        first_questions = [
            inquirer.List(
                "platform",
                message="What LLM (platform) are you setting?",
                choices=model_list.keys()
            )
        ]
        answers_1 = inquirer.prompt(first_questions)
        selected_platform = answers_1['platform']

        second_questions = [
            inquirer.Text(
                CONFIG_SEC_API_KEY,
                message=f"What is your {selected_platform} API key?",
            )
        ]
        answers_2 = inquirer.prompt(second_questions)
        if answers_2:
            return {
                "model": model_list[selected_platform],
                "platform": selected_platform.lower(),
                "api_key": answers_2[CONFIG_SEC_API_KEY],
                'temperature': 0.7,
                'max_tokens': 1500,
                'top_p': 1.0,
                'top_k': 32,
                'stop_sequences': 'None',
                'candidate_count': 1
            }
        else:
            return None
    except TypeError:
        return None


def qa_general(model_list: dict = CONFIG_LLM_LIST):
    """
    qa_general: ask the user to input the general configuration.

    Args:
        model_list: the list of models.
    """
    try:
        exe_questions = [
            inquirer.List(
                "platform",
                message="Which LLM (platform) are you setting as default?",
                choices=model_list.keys(),
            ),
            inquirer.Confirm(
                "auto_execute",
                message="Do you want to execute the generated command automatically?",
                default=True,
            )
        ]
        answers = inquirer.prompt(exe_questions)
        sc_answer = {"show_command": True}
        if answers["auto_execute"]:
            sc_question = [
                inquirer.Confirm(
                    "show_command",
                    message="Do you want to show the generated command?",
                    default=False,
                )
            ]
            sc_answer = inquirer.prompt(sc_question)

        general_config = {
            "platform": answers["platform"].lower(),
            "auto_execute": answers["auto_execute"],
            "show_command": sc_answer["show_command"],
            "storage_size": 2000
        }

        return general_config
    except TypeError:
        return None


def qa_confirm():
    """
    qa_execute: ask the user confirm whether to execute the generated commmand.
    """
    try:
        exe_questions = [
            inquirer.List(
                'execute',
                message="Choose your action",
                choices=[('Execute', 0), ('Abort', 1), ('Describe', 2)],
                carousel=False
            )
        ]
        answers = inquirer.prompt(exe_questions)
        return answers["execute"]
    except TypeError:
        return None
