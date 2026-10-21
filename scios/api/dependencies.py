def get_scios():
    """
    Dependency injection: return SciOS runtime instance.
    """
    from scios.runtime import SciOSRuntime
    return SciOSRuntime()
