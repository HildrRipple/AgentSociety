import re
import inspect
import ast
import asyncio
from typing import Any, Optional, Callable, Dict

from openai.types.chat import ChatCompletionMessageParam
from ..logger import get_logger
from ..memory import Memory

class FormatPrompt:
    """
    A class to handle the formatting of prompts based on a template,
    with support for system prompts and variable extraction.

    - **Attributes**:
        - `template` (str): The template string containing placeholders.
        - `system_prompt` (Optional[str]): An optional system prompt to add to the dialog.
        - `variables` (List[str]): A list of variable names extracted from the template.
        - `formatted_string` (str): The formatted string derived from the template and provided variables.
        - `bound_objects` (Dict[str, Any]): Dictionary of objects bound to the prompt for use in expressions.
    """

    def __init__(
        self, template: str, format_prompt: Optional[str] = None, system_prompt: Optional[str] = None, memory: Optional[Memory] = None
    ) -> None:
        """
        - **Description**:
            - Initializes the FormatPrompt with a template, an optional system prompt, and bound objects.

        - **Args**:
            - `template` (str): The string template with variable placeholders.
            - `system_prompt` (Optional[str], optional): An optional system prompt. Defaults to None.
            - `**bound_objects`: Named objects to bind to the prompt for use in expressions.
        """
        self.template = template
        self.format_prompt = format_prompt  # Store the format prompt
        self.system_prompt = system_prompt  # Store the system prompt
        self.variables = self._extract_variables()
        self.formatted_string = ""  # To store the formatted string
        self._associated_method = None  # To store associated method
        self._method_params = []  # To store method parameters
        self.memory = memory  # Store memory

    def _extract_variables(self) -> list[str]:
        """
        - **Description**:
            - Extracts variable names from the template string using regular expressions.
            - Looks for simple variables in the format {variable_name}.

        - **Returns**:
            - `List[str]`: A list of variable names found within the template.
        """
        return re.findall(r"\{(\w+)\}", self.template)

    def associate_with_method(self, method: Callable) -> "FormatPrompt":
        """
        - **Description**:
            - Associates this FormatPrompt instance with a class method.
            - Extracts parameter information from the method for later use.
            - Also captures parameter documentation if available.

        - **Args**:
            - `method` (Callable): The method to associate with this prompt.

        - **Returns**:
            - `FormatPrompt`: Self, for method chaining.
        """
        self._associated_method = method
        sig = inspect.signature(method)
        # Skip 'self' parameter for instance methods
        self._method_params = [
            param.name for param in sig.parameters.values() if param.name != "self"
        ]

        # Store parameter documentation if available
        self._param_docs = {}
        if hasattr(method, "__param_docs__"):
            self._param_docs = method.__param_docs__

        return self

    def get_param_documentation(self) -> Dict[str, str]:
        """
        - **Description**:
            - Returns documentation for parameters of the associated method.

        - **Returns**:
            - `Dict[str, str]`: A dictionary mapping parameter names to their documentation.
        """
        if not hasattr(self, "_param_docs"):
            return {}
        return self._param_docs

    def _is_safe_expression(self, expr: str) -> bool:
        """
        - **Description**:
            - Checks if an expression is safe to evaluate.
            - Prevents dangerous operations like imports, exec, eval, etc.

        - **Args**:
            - `expr` (str): The expression to check.

        - **Returns**:
            - `bool`: True if the expression is safe, False otherwise.
        """
        try:
            # Parse the expression into an AST
            tree = ast.parse(expr, mode="eval")

            # Define a visitor to check for unsafe operations
            class SafetyVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.is_safe = True

                def visit_Call(self, node):
                    # Check function name
                    if isinstance(node.func, ast.Name):
                        # Blacklist of unsafe functions
                        unsafe_funcs = [
                            "eval",
                            "exec",
                            "compile",
                            "open",
                            "__import__",
                            "globals",
                            "locals",
                        ]
                        if node.func.id in unsafe_funcs:
                            self.is_safe = False
                    self.generic_visit(node)

                def visit_Import(self, node):
                    self.is_safe = False

                def visit_ImportFrom(self, node):
                    self.is_safe = False

            # Check the expression
            visitor = SafetyVisitor()
            visitor.visit(tree)
            return visitor.is_safe
        except SyntaxError:
            # If we can't parse it, it's not safe
            return False

    async def _eval_expr(self, expr: str, context: dict) -> Any:
        """
        - **Description**:
            - Evaluates expressions in the format ${profile.xxx}, ${status.xxx}, or ${context.xxx}.
            - Retrieves values from memory or context dictionary.

        - **Args**:
            - `expr` (str): The expression to evaluate.
            - `context` (dict): The evaluation context.

        - **Returns**:
            - `Any`: The result of the expression evaluation.
        """
        # Parse the expression to determine which type it is
        if expr.startswith("profile."):
            key = expr[len("profile."):]
            if self.memory:
                return await self.memory.status.get(key)
            else:
                return "Don't know"
        elif expr.startswith("status."):
            key = expr[len("status."):]
            if self.memory:
                return await self.memory.status.get(key)
            else:
                return "Don't know"
        elif expr.startswith("context."):
            key = expr[len("context."):]
            if context:
                return context.get(key)
            else:
                return "Don't know"
        else:
            raise ValueError(f"Invalid expression format: {expr}. Must be one of: profile.xxx, status.xxx, context.xxx")

    async def format(
        self,
        context: Optional[dict] = None,
        **kwargs,
    ) -> str:
        """
        - **Description**:
            - Formats the template string using the provided context and keyword arguments.
            - Supports simple variables {var} for direct substitution.
            - Supports complex expressions ${expression} in three formats:
              - ${profile.xxx}: Retrieves values from memory.profile
              - ${status.xxx}: Retrieves values from memory.status
              - ${context.xxx}: Retrieves values from the provided context dictionary

        - **Args**:
            - `context` (Optional[dict]): Dictionary containing context values.
            - `**kwargs`: Variable names and their corresponding values to format the template.

        - **Returns**:
            - `str`: The formatted string.

        - **Raises**:
            - `KeyError`: If a placeholder in the template does not have a corresponding key in kwargs.
            - `ValueError`: If an expression has an invalid format.
        """
        # Create a dictionary to hold all formatting variables
        format_vars = {}

        # First add explicitly provided kwargs, these take highest precedence
        for key, value in kwargs.items():
            if key in self.variables:
                format_vars[key] = value

        eval_context = context if context else {}

        # Handle complex expressions in the template using ${expression} syntax
        complex_pattern = r"\$\{([^}]+?)\}"
        result = self.template

        # Find all complex expressions
        matches = re.finditer(complex_pattern, self.template)
        for match in matches:
            expr = match.group(1).strip()
            full_match = match.group(0)

            try:
                eval_result = await self._eval_expr(expr, eval_context)
                result = result.replace(full_match, str(eval_result) if eval_result is not None else "")
            except Exception as e:
                print(f"Error evaluating expression '{expr}': {str(e)}")
                # Keep the original expression in case of error

        # Then format simple variables using {var} syntax
        try:
            self.formatted_string = result.format(**format_vars)
            return self.formatted_string
        except KeyError as e:
            raise KeyError(f"Missing required variable in template: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting template: {e}")

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
        if self.format_prompt:
            dialog.append(
                {"role": "user", "content": self.formatted_string + "\n" + self.format_prompt}
            )
        else:
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
        print(f"Prompt Template: {self.template}")
        print(f"Format Prompt: {self.format_prompt}")
        print(f"System Prompt: {self.system_prompt}")  # Log the system prompt
        print(f"Variables: {self.variables}")
        print(f"Formatted String: {self.formatted_string}")  # Log the formatted string
