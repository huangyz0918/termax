from pydantic import Field
from instructor import OpenAISchema

from termax.prompt import process_mac_script


class MacFunction(OpenAISchema):
    """
    Executes Apple Script on macOS and returns the output (result).
    Can be used for actions like: draft (prepare) an email, show calendar events, create a note.
    """

    script: str = Field(
        ...,
        example='tell application "Terminal" to display dialog "Hello World"',
        descriptions="Apple Script to execute.",
    )

    class Config:
        title = "execute_apple_script"

    @classmethod
    def execute(cls, script):
        return " ".join(["osascript", "-e", process_mac_script(script)])
