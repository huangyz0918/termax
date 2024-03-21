import inquirer
from termax.utils.const import *

class QA:
    """
    QA: Command Line Question Answering for Config Info.
    """
    
    def __init__(self):
        pass
    
    def platform_qa(self, model_list : str = CONFIG_LLM_LIST):
        first_questions = [
            inquirer.List(
                "platform",
                message="What LLM (platform) are you setting?",
                choices=model_list.keys(),
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
        platform_config = {
            "model": model_list[selected_platform],
            "platform": selected_platform.lower(),
            "api_key": answers_2[CONFIG_SEC_API_KEY] if answers_2 else None,
            'temperature': 0.7,
            'max_tokens' : 1500,
            'top_p' : 1.0,
            'top_k' : 32,
            'stop_sequences' : 'None',
            'candidate_count' : 1
        }
        
        return platform_config
    
    def general_qa(self, model_list : str = CONFIG_LLM_LIST):
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
            ),
            inquirer.Confirm(
                "show_command",
                message="Do you want to show the generated command?",
                default=False,
            )
        ]
        answers = inquirer.prompt(exe_questions)
        general_config = {
            "platform": answers["platform"].lower(),
            "auto_execute": answers["auto_execute"],
            "show_command": answers["show_command"] if answers["auto_execute"] == True else True
        }
        
        return general_config
        
        