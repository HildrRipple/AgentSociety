import re
from typing import Any, Optional, Union, overload

from openai.types.chat import ChatCompletionMessageParam


class FormatPrompt:
    """
    A class to handle the formatting of prompts based on a template,
    with support for system prompts and variable extraction.

    - **Attributes**:
        - `template` (str): The template string containing placeholders.
        - `system_prompt` (Optional[str]): An optional system prompt to add to the dialog.
        - `variables` (List[str]): A list of variable names extracted from the template.
        - `formatted_string` (str): The formatted string derived from the template and provided variables.
    """

    def __init__(self, template: str, system_prompt: Optional[str] = None) -> None:
        """
        - **Description**:
            - Initializes the FormatPrompt with a template and an optional system prompt.

        - **Args**:
            - `template` (str): The string template with variable placeholders.
            - `system_prompt` (Optional[str], optional): An optional system prompt. Defaults to None.
        """
        self.template = template
        self.system_prompt = system_prompt  # Store the system prompt
        self.variables = self._extract_variables()
        self.formatted_string = ""  # To store the formatted string

    def _extract_variables(self) -> list[str]:
        """
        - **Description**:
            - Extracts variable names from the template string using regular expressions.

        - **Returns**:
            - `List[str]`: A list of variable names found within the template.
        """
        return re.findall(r"\{(\w+)\}", self.template)

    def format(self, agent: Optional[Any] = None, block: Optional[Any] = None, **kwargs) -> str:
        """
        - **Description**:
            - Formats the template string using the provided agent, block, or keyword arguments.

        - **Args**:
            - `agent` (Optional[Agent]): Agent object containing attributes to format the template.
            - `block` (Optional[Block]): Block object containing attributes to format the template.
            - `**kwargs`: Variable names and their corresponding values to format the template.

        - **Returns**:
            - `str`: The formatted string.

        - **Raises**:
            - `KeyError`: If a placeholder in the template does not have a corresponding key in kwargs.
        """
        # Create a dictionary to hold all formatting variables
        format_vars = {}
        
        # Extract variables from agent if provided
        if agent is not None:
            # Add agent attributes that match template variables
            for var in self.variables:
                if var in agent.__class__.get_functions:
                    format_vars[var] = agent._getx(var)
        
        # Extract variables from block if provided
        if block is not None:
            # Add block attributes that match template variables
            for var in self.variables:
                if var in block.__class__.get_functions:
                    format_vars[var] = block._getx(var)
        
        # Add any explicitly provided kwargs, these take precedence
        for key, value in kwargs.items():
            if key in self.variables:
                format_vars[key] = value
        
        # Format the template with the collected variables
        self.formatted_string = self.template.format(**format_vars)
        return self.formatted_string

    def to_dialog(self) -> list[ChatCompletionMessageParam]:
        """
        - **Description**:
            - Converts the formatted prompt and optional system prompt into a dialog format suitable for chat systems.

        - **Returns**:
            - `List[Dict[str, str]]`: A list representing the dialog with roles and content.
        """
        dialog = []
        if self.system_prompt:
            dialog.append(
                {"role": "system", "content": self.system_prompt}
            )  # Add system prompt if it exists
        dialog.append(
            {"role": "user", "content": self.formatted_string}
        )  # Add user content
        return dialog

    def log(self) -> None:
        """
        - **Description**:
            - Logs the details of the FormatPrompt instance, including the template,
              system prompt, extracted variables, and formatted string.
        """
        print(f"FormatPrompt: {self.template}")
        print(f"System Prompt: {self.system_prompt}")  # Log the system prompt
        print(f"Variables: {self.variables}")
        print(f"Formatted String: {self.formatted_string}")  # Log the formatted string
