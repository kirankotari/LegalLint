from builtins import Exception, Warning

class LegalLintError(Exception):
    """Base class for all LegalLint exceptions."""
    def __init__(self, message=None):
        super().__init__(message or "LegalLint: license compliance check failed.")


class LegalLintWarning(Warning):
    """Warning message for legallint license compliance."""
    def __init__(self, message=None):
        super().__init__(message or "LegalLint: License compliance warning.")


class LegalLintInfo:
    """Informational message for legallint license compliance."""
    def __init__(self, message=None):
        self.message = message or "LegalLint: License compliance successful."

    def __str__(self):
        return self.message