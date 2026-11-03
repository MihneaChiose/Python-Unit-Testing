"""Typed domain models for rental eligibility evaluation."""

from dataclasses import dataclass
from enum import Enum


class BookingErrorCode(str, Enum):
    """Stable identifiers that clients can handle independently of messages."""

    INVALID_CLIENT_AGE = "invalid_client_age"
    UNDERAGE = "underage"
    INVALID_LICENSE_STATUS = "invalid_license_status"
    NO_LICENSE = "no_license"
    INVALID_DRIVING_EXPERIENCE = "invalid_driving_experience"
    INVALID_RENTAL_PERIOD = "invalid_rental_period"
    INVALID_BUDGET = "invalid_budget"
    INVALID_SEAT_REQUIREMENT = "invalid_seat_requirement"
    INVALID_CARS_COLLECTION = "invalid_cars_collection"
    NO_ELIGIBLE_CARS = "no_eligible_cars"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class BookingError:
    code: BookingErrorCode
    message: str


@dataclass(frozen=True, slots=True)
class Car:
    """A vehicle available for evaluation (not a database entity yet)."""

    model: str
    category: str
    price_per_day: int | float
    available: bool
    horsepower: int
    seats: int

    def to_mapping(self) -> dict[str, object]:
        """Convert to the input shape accepted by the legacy processor."""
        return {
            "model": self.model,
            "category": self.category,
            "price_per_day": self.price_per_day,
            "available": self.available,
            "horsepower": self.horsepower,
            "seats": self.seats,
        }


@dataclass(frozen=True, slots=True)
class BookingRequest:
    """Typed request for the new evaluation interface."""

    cars: tuple[Car, ...]
    client_age: int
    has_license: bool
    driving_experience_years: int
    rental_days: int
    budget: float
    min_seats_needed: int


@dataclass(frozen=True, slots=True)
class BookingOption:
    model: str
    category: str
    total_price: int | float
    horsepower: int
    seats: int


@dataclass(frozen=True, slots=True)
class BookingResult:
    """Consistent result: options for success, or one structured error."""

    options: tuple[BookingOption, ...]
    error: BookingError | None = None

    def __post_init__(self) -> None:
        if self.error is None and not self.options:
            raise ValueError("Successful results must contain at least one option")
        if self.error is not None and self.options:
            raise ValueError("Failed results cannot contain options")

    @property
    def success(self) -> bool:
        return self.error is None
