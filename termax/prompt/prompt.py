from .memory import Memory
from termax.utils.metadata import *
from termax.utils import CONFIG_SEC_OPENAI


class Prompt:
    def __init__(self, memory):
        # TODO: make the sync of system related metadata once happened at the initialization
        self.system_metadata = get_system_metadata()
        self.path_metadata = get_path_metadata()
        self.command_history = get_command_history()

        # share the same memory instance.
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory

    def nl2commands(self, text: str, model: str = CONFIG_SEC_OPENAI):
        # query the history database to get similar samples
        samples = self.memory.query([text], n_results=5)
        metadatas = samples['metadatas'][0]
        documents = samples['documents'][0]
        distances = samples['distances'][0]

        # construct a string that contains the samples in a human-readable format
        sample_string = ""
        for i in range(len(documents)):
            sample_string += f"""
            User Input: {documents[i]}
            Generated Commands: {metadatas[i]['response']}
            Distance Score: {distances[i]}
            Date: {metadatas[i]['created_at']}\n
            """

        # refresh the metadata
        self.command_history = get_command_history()
        # TODO: add more models specific prompt
        if model == CONFIG_SEC_OPENAI:
            return f"""
            You are an shell expert, you can convert this text to shell commands.\n
            
            1. Please provide only shell commands for os without any description.
            2. Ensure the output is a valid shell command.
            3. If multiple steps required try to combine them together.
            
            Here are some rules you need to follow:\n
            
            1. The commands should be able to run on the current system according to the system information.
            2. The files in the commands (if any) should be available in the path, according to the path information.
            3. The CLI application should be installed in the system (check the path information).
            
            Here are some information you may need to know:\n
            
            \nCurrent system information (in dict format): {self.system_metadata} \n
            
            \nThe user's system PATH information (in dict format): {self.path_metadata} \n
            
            \nThe user's command history (in dict format): {self.command_history} \n
            
            Here are some similar commands generated before:\n
            
            {sample_string}
            
            The output shell commands is (please replace the `{{commands}}` with the actual commands):
            
            Commands: ${{commands}}
            """
