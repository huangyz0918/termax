import subprocess

from instructor import OpenAISchema


class GitFunction(OpenAISchema):
    """
    Executes a git diff command and returns the output (result).
    """

    class Config:
        title = "get_git_diff"

    @classmethod
    def execute(cls):
        try:
            result = subprocess.run(['git', 'diff'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return None

            return result.stdout
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
