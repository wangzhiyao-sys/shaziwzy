from typing import Any, Dict

from prompts import YA_MCPServer_Prompt


@YA_MCPServer_Prompt(
    name="greet_user",
    title="Greeting Prompt",
    description="Generate a greeting message. Use this to test the prompt system or create welcome messages.",
)
async def hello_prompt(name: str) -> str:
    """Generate a greeting message for the user.

    Args:
        name (str): The user's name.

    Returns:
        str: A greeting message.

    Example:
        Input: name="Alice"
        Output: "Hello, Alice! Welcome to MCP-PolyGame-Agent."
    """
    return f"Hello, {name}! Welcome to MCP-PolyGame-Agent - a role-aware multi-party game reasoning system for Werewolf game."
