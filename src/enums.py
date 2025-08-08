from enum import Enum


class EventType(str, Enum):
    arrival = "arrival"
    departure = "departure"
