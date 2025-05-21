import re
import inspect
import ast
import asyncio
from typing import Any, Optional, Union, overload, Callable, Dict, List, Type

from openai.types.chat import ChatCompletionMessageParam
from ..logger import get_logger

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

    def __init__(self, template: str, system_prompt: Optional[str] = None, **bound_objects) -> None:
        """
        - **Description**:
            - Initializes the FormatPrompt with a template, an optional system prompt, and bound objects.

        - **Args**:
            - `template` (str): The string template with variable placeholders.
            - `system_prompt` (Optional[str], optional): An optional system prompt. Defaults to None.
            - `**bound_objects`: Named objects to bind to the prompt for use in expressions.
        """
        self.template = template
        self.system_prompt = system_prompt  # Store the system prompt
        self.variables = self._extract_variables()
        self.formatted_string = ""  # To store the formatted string
        self._associated_method = None  # To store associated method
        self._method_params = []  # To store method parameters
        self.bound_objects = bound_objects  # Store bound objects

    def bind(self, **objects) -> 'FormatPrompt':
        """
        - **Description**:
            - Binds additional objects to the prompt for use in expressions.
            - These objects will be available in the template by their given names.

        - **Args**:
            - `**objects`: Named objects to bind to the prompt.

        - **Returns**:
            - `FormatPrompt`: Self, for method chaining.
        """
        self.bound_objects.update(objects)
        return self

    def _extract_variables(self) -> list[str]:
        """
        - **Description**:
            - Extracts variable names from the template string using regular expressions.
            - Looks for simple variables in the format {variable_name}.

        - **Returns**:
            - `List[str]`: A list of variable names found within the template.
        """
        return re.findall(r"\{(\w+)\}", self.template)

    def associate_with_method(self, method: Callable) -> 'FormatPrompt':
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
            param.name for param in sig.parameters.values() 
            if param.name != 'self'
        ]
        
        # Store parameter documentation if available
        self._param_docs = {}
        if hasattr(method, "__param_docs__"):
            self._param_docs = method.__param_docs__
            
        return self
    
    def get_available_variables(self) -> Dict[str, List[str]]:
        """
        - **Description**:
            - Returns information about available variables and their possible sources.
            - Includes parameter documentation if available.
            - Now also includes bound objects as possible sources.

        - **Returns**:
            - `Dict[str, List[str]]`: A dictionary mapping variable names to their possible sources and documentation.
        """
        result = {}
        for var in self.variables:
            sources = []
            if self._associated_method and var in self._method_params:
                method_name = self._associated_method.__name__
                source = f"method parameter: {method_name}({var})"
                
                # Add documentation if available
                if var in getattr(self, "_param_docs", {}) and self._param_docs[var]:
                    source += f" - {self._param_docs[var]}"
                    
                sources.append(source)
            
            # Add bound objects as possible sources
            if var in self.bound_objects:
                sources.append(f"bound object: {var}")
                
            result[var] = sources
        return result

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
            tree = ast.parse(expr, mode='eval')
            
            # Define a visitor to check for unsafe operations
            class SafetyVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.is_safe = True
                
                def visit_Call(self, node):
                    # Check function name
                    if isinstance(node.func, ast.Name):
                        # Blacklist of unsafe functions
                        unsafe_funcs = ['eval', 'exec', 'compile', 'open', '__import__', 'globals', 'locals']
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

    async def _eval_async_expr(self, expr: str, context: dict) -> Any:
        """
        - **Description**:
            - Evaluates an expression that might contain async calls.
            - Directly checks if methods are coroutine functions and awaits them if needed.

        - **Args**:
            - `expr` (str): The expression to evaluate.
            - `context` (dict): The evaluation context.

        - **Returns**:
            - `Any`: The result of the expression evaluation.
        """
        # First try direct evaluation for simple expressions
        try:
            # Evaluate the expression
            result = eval(expr, {"__builtins__": {}}, context)
            
            # If the result is awaitable, await it
            if inspect.isawaitable(result):
                return await result
            return result
        except Exception as e:
            # If direct evaluation fails, try more complex approach
            try:
                # Create a temporary async function to evaluate the expression
                # This allows us to use await inside the expression
                exec_globals = {"__builtins__": {}, "asyncio": asyncio}
                
                # Add all context variables to the globals
                for key, value in context.items():
                    exec_globals[key] = value
                
                # Create an async function that will execute the expression
                exec_code = f"""
async def _temp_eval_func():
    return {expr}
"""
                # Compile and execute the function definition
                exec(exec_code, exec_globals)
                
                # Call the function and await its result
                result = await exec_globals["_temp_eval_func"]()
                return result
            except Exception as e2:
                raise ValueError(f"Error evaluating expression '{expr}': {str(e2)}")

    async def format(self, agent: Optional[Any] = None, block: Optional[Any] = None, 
                    method_args: Optional[dict] = None, **kwargs) -> str:
        """
        - **Description**:
            - Formats the template string using the provided agent, block, method arguments, or keyword arguments.
            - Supports both simple variables {var} for direct substitution.
            - Supports complex expressions ${expression} for evaluation.
            - Automatically detects and awaits async functions in expressions.
            - Can use bound objects in expressions (e.g., ${environment.get("weather")}).
            - Attempts to find variable values from multiple sources in order of precedence:
              1. Explicitly provided kwargs
              2. Method arguments (if associated method and method_args provided)
              3. Agent attributes or memory
              4. Block attributes
              5. Bound objects

        - **Args**:
            - `agent` (Optional[Any]): Agent object containing attributes to format the template.
            - `block` (Optional[Any]): Block object containing attributes to format the template.
            - `method_args` (Optional[dict]): Arguments passed to the associated method.
            - `**kwargs`: Variable names and their corresponding values to format the template.

        - **Returns**:
            - `str`: The formatted string.

        - **Raises**:
            - `KeyError`: If a placeholder in the template does not have a corresponding key in kwargs.
            - `ValueError`: If an expression is deemed unsafe or evaluation fails.
        """
        # Create a dictionary to hold all formatting variables
        format_vars = {}
        
        # First try to get values from method arguments if provided
        if method_args is not None and self._associated_method is not None:
            for var in self.variables:
                if var in self._method_params and var in method_args:
                    format_vars[var] = method_args[var]
        
        # Then try to get values from agent if provided
        if agent is not None:
            for var in self.variables:
                if var not in format_vars:  # Only try if not already found
                    try:
                        # Try to get from agent functions first
                        if var in agent.__class__.get_functions:
                            format_vars[var] = await agent._getx(var)
                        # Then try agent memory
                        else:
                            try:
                                format_vars[var] = await agent.memory.status.get(var)
                            except Exception:
                                # Just continue if not found in memory
                                pass
                    except Exception as e:
                        # Log the error but continue
                        print(f"Error getting variable '{var}' from agent: {str(e)}")
        
        # Then try to get values from block if provided
        if block is not None:
            for var in self.variables:
                if var not in format_vars and var in block.__class__.get_functions:
                    try:
                        format_vars[var] = await block._getx(var)
                    except Exception as e:
                        print(f"Error getting variable '{var}' from block: {str(e)}")
        
        # Then try to get values from bound objects
        for var in self.variables:
            if var not in format_vars and var in self.bound_objects:
                format_vars[var] = self.bound_objects[var]
        
        # Finally add explicitly provided kwargs, these take highest precedence
        for key, value in kwargs.items():
            if key in self.variables:
                format_vars[key] = value

        eval_context = {
            'agent': agent,
            'block': block,
            **self.bound_objects,  # Include bound objects in the context
            **(method_args if method_args else {}),
            **kwargs,
        }
        
        # Handle complex expressions in the template using ${expression} syntax
        complex_pattern = r"\$\{([^}]+?)\}"
        result = self.template
        
        # Find all complex expressions
        matches = re.finditer(complex_pattern, self.template)
        for match in matches:
            expr = match.group(1).strip()
            full_match = match.group(0)
            
            if not self._is_safe_expression(expr):
                raise ValueError(f"Unsafe expression detected: {expr}")
            
            try:
                eval_result = await self._eval_async_expr(expr, eval_context)
                result = result.replace(full_match, str(eval_result))
            except Exception as e:
                print(f"Error evaluating expression '{expr}': {str(e)}")
                # Keep the original expression
        
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
