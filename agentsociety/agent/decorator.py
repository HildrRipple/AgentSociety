def register_get(description: str):
    """
    Registers a method as an available function.
    
    - **Description**:
        - Function that registers a method as an available function with the given name and description.
    
    - **Args**:
        - `function_name` (str): The name of the function to register.
        - `description` (str): Description of what the function does.
    
    - **Returns**:
        - `decorator` (Callable): The decorator function.
    """
    def decorator(method):
        # Get the class from the method when it's being defined
        def wrapper(self, *args, **kwargs):
            return method(self, *args, **kwargs)
        
        # Store the registration info to be processed later
        wrapper._get_info = {
            "description": description,
            "original_method": method
        }
        return wrapper
    return decorator