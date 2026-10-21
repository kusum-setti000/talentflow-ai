class InputError(ValueError):
    """User can resolve this by changing the input."""


class SourceUnavailable(InputError):
    """The remote job source cannot be read safely or reliably."""


class AnalysisError(RuntimeError):
    """A model call failed or returned an unusable response."""
