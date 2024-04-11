import shlex
import subprocess

from instructor import OpenAISchema
from pydantic import Field


class MacFunction(OpenAISchema):
    """
    Executes Apple Script on macOS and returns the output (result).
    Can be used for actions like: draft (prepare) an email, show calendar events, create a note.
    """

    script: str = Field(
        ...,
        example='tell application "Finder" to get the name of every disk',
        descriptions="Apple Script to execute.",
    )

    class Config:
        title = "execute_apple_script"

    @classmethod
    def execute(cls, script):
        commands = ["osascript", "-e", script]
        return " ".join(shlex.quote(part) for part in commands)
