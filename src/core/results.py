class ValidationResult:
    def __init__(self, success: bool, errors: list = None, message: str = ""):
        self.success = success
        self.errors = errors or []
        self.message = message
    def __bool__(self):
        return self.success

class SimulationResult:
    def __init__(self, success: bool, message: str = "", details: dict = None, error: str = None):
        self.success = success
        self.message = message
        self.details = details or {}
        self.error = error
    def __bool__(self):
        return self.success 