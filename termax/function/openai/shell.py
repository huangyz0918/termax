import subprocess

from instructor import OpenAISchema
from pydantic import Field


class ShellFunction(OpenAISchema):
    """
    Executes a shell command and returns the output (result).
    """

    shell_command: str = Field(
        ...,
        example="ls -la",
        descriptions="Shell command to execute.",
    )

    class Config:
        title = "execute_shell_command"

    @classmethod
    def execute(cls, shell_command) -> str:
        return shell_command