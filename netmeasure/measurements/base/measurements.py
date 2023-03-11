"""
Honesty Box Measurement

A framework for measuring things and producing structured results.
Copyright (C) 2019 Honesty Box Engineering
engineering@honestybox.com.au

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import typing

from netmeasure.measurements.base.results import MeasurementResult


class BaseMeasurement:
    """Interface for creating measurements.

    This base class is designed to be sub-classed and used as an
    interface for creating new measurement types.
    """

    def __init__(self, id):
        """Initialisation of a base measurement

        :param id: A unique identifier for the measurement.
        """
        super(BaseMeasurement, self).__init__()
        self.id = id

    def measure(self):
        """Perform the measurement and return the measurement results."""
        raise NotImplementedError
