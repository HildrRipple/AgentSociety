import inspect

def register_get(description: str):
    """
    Registers a method as an available function.
    
    - **Description**:
        - Function that registers a method as an available function with the given name and description.
    
    - **Args**:
        - `description` (str): Description of what the function does.
    
    - **Returns**:
        - `decorator` (Callable): The decorator function.
    """
    def decorator(method):
        # Check if the method is async
        is_async = inspect.iscoroutinefunction(method)
        
        if is_async:
            # For async methods, preserve the async nature
            async def async_wrapper(self, *args, **kwargs):
                return await method(self, *args, **kwargs)
            wrapper = async_wrapper
        else:
            # For regular methods
            def sync_wrapper(self, *args, **kwargs):
                return method(self, *args, **kwargs)
            wrapper = sync_wrapper
        
        # Store the registration info to be processed later
        wrapper._get_info = {
            "function_name": method.__name__,
            "description": description,
            "original_method": method,
            "is_async": is_async
        }
        return wrapper
    return decorator