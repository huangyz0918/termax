from termax.utils.metadata import *


class Prompt:
    def __init__(self):
        self.git_metadata = get_git_metadata()
        self.system_metadata = get_system_metadata()
        self.python_metadata = get_python_metadata()
        self.gpu_metadata = get_gpu_metadata()
        self.path_metadata = get_path_metadata()
        self.command_history = get_command_history()

    def nl2commands(self):
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
        
        \nGit information in the current directory (in dict format): {self.git_metadata} \n
        
        \nThe Python environment information (in dict format): {self.python_metadata} \n
        
        \nThe GPU environment information (empty means no available GPUs) (in dict format): {self.gpu_metadata} \n
        
        \nThe user's system PATH information (in dict format): {self.path_metadata} \n
        
        \nThe user's command history (in dict format): {self.command_history} \n
        
        The output shell commands is (please replace the `{{commands}}` with the actual commands):
        
        Commands: ${{commands}}
        """
