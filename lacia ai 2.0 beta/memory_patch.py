"""
Memory system patch for Lacia AI
Fixes sequence index slice errors
"""

def safe_memory_slice(memory_data, slice_obj=None):
    """
    Safely handle memory slicing operations
    Fixes: sequence index must be integer, not 'slice'
    """
    if not isinstance(memory_data, (list, tuple)):
        return []
    
    if slice_obj is None:
        return list(memory_data)
    
    if isinstance(slice_obj, slice):
        return memory_data[slice_obj]
    elif isinstance(slice_obj, int):
        try:
            return [memory_data[slice_obj]]
        except IndexError:
            return []
    elif isinstance(slice_obj, (list, tuple)) and len(slice_obj) == 2:
        start, end = slice_obj
        return memory_data[start:end]
    else:
        return list(memory_data)

def safe_memory_access(memory_list, index):
    """
    Safely access memory by index
    """
    if not isinstance(memory_list, (list, tuple)):
        return None
    
    if isinstance(index, int):
        try:
            return memory_list[index]
        except IndexError:
            return None
    
    return None

def patch_memory_retrieval(original_function):
    """
    Decorator to patch memory retrieval functions
    """
    def wrapper(*args, **kwargs):
        try:
            return original_function(*args, **kwargs)
        except (IndexError, TypeError) as e:
            if "sequence index must be integer" in str(e):
                # Handle slice error
                if len(args) > 1 and hasattr(args[1], '__getitem__'):
                    return safe_memory_slice(args[0], args[1])
            return []
    return wrapper

# Usage in core/cognition/processor.py:
# Add this import: from memory_patch import patch_memory_retrieval, safe_memory_slice
# Then wrap problematic functions with @patch_memory_retrieval
