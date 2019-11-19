from enum import Enum


class NetworkUnit(Enum):
    """Anticipated units for a network style of measurement."""

    kilobit_per_second = "kbit/s"
    megabit_per_second = "Mbit/s"
    kibibit_per_second = "Kibit/s"
    mebibit_per_second = "Mibit/s"


class StorageUnit(Enum):
    """Anticipated units for a storage style of measurement."""

    bit = "bit"
    bytes = "B"
    kilobit = "kbit"
    megabit = "Mbit"
    kibibit = "Kibit"
    mebibit = "Mibit"
    kilobyte = "kB"
    megabyte = "MB"
    kibibyte = "KiB"
    mebibyte = "MiB"


class TimeUnit(Enum):
    millisecond = "ms"
    second = "s"
    minute = "m"
    hour = "h"
    day = "d"


class RatioUnit(Enum):
    percentage = "%"
