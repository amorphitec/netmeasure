import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Error:
    """An error format for use with `MeasurementResult`.

    This data class is designed to be used with the `MeasurementResult`
    data class and its' subclasses to describe any errors that
    occurred in a measurement.

    :param key: A key to describe the error type.
    :param description: A human readable description of the encountered
    error.
    :param traceback: The traceback or outputs of a command that caused
    the error to occur.
    """

    key: str
    description: str
    traceback: str


@dataclass(frozen=True)
class MeasurementResult:
    """ "A standard interface for measurement results

    :param id: A unique identifier for the measurement result.
    :param errors: The errors that occurred while attempting to take
    the measurement.
    """

    id: str
    errors: typing.List[Error]
