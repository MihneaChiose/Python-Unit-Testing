"""Business rules for evaluating car rental requests."""

from collections.abc import Iterable, Mapping
from math import isfinite
from typing import Any, ClassVar

from .models import (
    BookingError,
    BookingErrorCode,
    BookingOption,
    BookingRequest,
    BookingResult,
)


class RentalBookingProcessor:
    """Select eligible cars and calculate their rental prices."""

    REQUIRED_CAR_FIELDS = frozenset(
        {"model", "category", "price_per_day", "available", "horsepower", "seats"}
    )
    VALID_CATEGORIES = frozenset({"economy", "standard", "premium"})
    ERROR_CODES: ClassVar[dict[str, BookingErrorCode]] = {
        "Invalid client age": BookingErrorCode.INVALID_CLIENT_AGE,
        "Client is underage": BookingErrorCode.UNDERAGE,
        "Invalid license status": BookingErrorCode.INVALID_LICENSE_STATUS,
        "Client has no valid license": BookingErrorCode.NO_LICENSE,
        "Invalid driving experience": BookingErrorCode.INVALID_DRIVING_EXPERIENCE,
        "Invalid rental period": BookingErrorCode.INVALID_RENTAL_PERIOD,
        "Invalid budget": BookingErrorCode.INVALID_BUDGET,
        "Invalid seat requirement": BookingErrorCode.INVALID_SEAT_REQUIREMENT,
        "Invalid cars collection": BookingErrorCode.INVALID_CARS_COLLECTION,
        "No cars available for this client": BookingErrorCode.NO_ELIGIBLE_CARS,
    }
    YOUNG_DRIVER_FEE_PER_DAY = 20
    RESTRICTED_DRIVER_MAX_HORSEPOWER = 120

    def process_booking(
        self,
        cars: Iterable[Mapping[str, Any]],
        client_age: int,
        has_license: bool,
        driving_experience_years: int,
        rental_days: int,
        budget: float,
        min_seats_needed: int,
    ) -> list[dict[str, Any]] | str:
        """Return eligible vehicles or a validation/status message.

        Invalid vehicle entries are skipped; invalid requests are rejected.
        """
        error = self._validate_request(
            client_age,
            has_license,
            driving_experience_years,
            rental_days,
            budget,
            min_seats_needed,
        )
        if error is not None:
            return error

        if not isinstance(cars, Iterable) or isinstance(cars, (str, bytes, Mapping)):
            return "Invalid cars collection"

        available_options: list[dict[str, Any]] = []
        for car in cars:
            if not self._passes_vehicle_filters(
                car, client_age, driving_experience_years, min_seats_needed
            ):
                continue

            total_price = self._calculate_total_price(car, client_age, rental_days)
            if isinstance(total_price, float) and not isfinite(total_price):
                continue
            if total_price > budget:
                continue

            if not self._meets_category_requirements(
                car, client_age, driving_experience_years
            ):
                continue

            available_options.append(self._build_option(car, total_price))

        if not available_options:
            return "No cars available for this client"
        return available_options

    def evaluate_booking(self, request: BookingRequest) -> BookingResult:
        """Return a typed result while reusing the tested legacy business rules.

        This is a transitional adapter: ``process_booking`` keeps its existing
        signature and output for callers and tests that already depend on it.
        """
        legacy_result = self.process_booking(
            cars=(car.to_mapping() for car in request.cars),
            client_age=request.client_age,
            has_license=request.has_license,
            driving_experience_years=request.driving_experience_years,
            rental_days=request.rental_days,
            budget=request.budget,
            min_seats_needed=request.min_seats_needed,
        )
        if isinstance(legacy_result, str):
            return BookingResult(
                options=(),
                error=BookingError(
                    code=self.ERROR_CODES.get(legacy_result, BookingErrorCode.UNKNOWN),
                    message=legacy_result,
                ),
            )
        return BookingResult(
            options=tuple(BookingOption(**option) for option in legacy_result)
        )

    @staticmethod
    def _is_integer(value: object) -> bool:
        """Accept integer values, but not booleans (which subclass int)."""
        return isinstance(value, int) and not isinstance(value, bool)

    @staticmethod
    def _is_positive_amount(value: object) -> bool:
        """Accept positive finite int/float amounts, excluding booleans."""
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and value > 0
            and (not isinstance(value, float) or isfinite(value))
        )

    @classmethod
    def _validate_request(
        cls,
        client_age: int,
        has_license: bool,
        driving_experience_years: int,
        rental_days: int,
        budget: float,
        min_seats_needed: int,
    ) -> str | None:
        """Validate request values while keeping existing error messages."""
        if not cls._is_integer(client_age):
            return "Invalid client age"
        if client_age < 18:
            return "Client is underage"
        if not isinstance(has_license, bool):
            return "Invalid license status"
        if not has_license:
            return "Client has no valid license"
        if (
            not cls._is_integer(driving_experience_years)
            or driving_experience_years < 0
        ):
            return "Invalid driving experience"
        if not cls._is_integer(rental_days) or rental_days <= 0:
            return "Invalid rental period"
        if not cls._is_positive_amount(budget):
            return "Invalid budget"
        if not cls._is_integer(min_seats_needed) or min_seats_needed <= 0:
            return "Invalid seat requirement"
        return None

    def _passes_vehicle_filters(
        self,
        car: Mapping[str, Any],
        client_age: int,
        driving_experience_years: int,
        min_seats_needed: int,
    ) -> bool:
        """Check required vehicle fields and all eligibility-related filters."""
        if not isinstance(car, Mapping) or not self.REQUIRED_CAR_FIELDS.issubset(car):
            return False
        if not isinstance(car["model"], str) or not car["model"].strip():
            return False
        if (
            not isinstance(car["category"], str)
            or car["category"] not in self.VALID_CATEGORIES
        ):
            return False
        if not isinstance(car["available"], bool) or not car["available"]:
            return False
        if not self._is_integer(car["seats"]) or car["seats"] <= 0:
            return False
        if not self._is_integer(car["horsepower"]) or car["horsepower"] <= 0:
            return False
        if not self._is_positive_amount(car["price_per_day"]):
            return False
        if car["seats"] < min_seats_needed:
            return False
        return not (
            (client_age < 21 or driving_experience_years < 2)
            and car["horsepower"] > self.RESTRICTED_DRIVER_MAX_HORSEPOWER
        )

    def _calculate_total_price(
        self, car: Mapping[str, Any], client_age: int, rental_days: int
    ) -> float:
        """Calculate the total amount, including the young-driver surcharge."""
        base_price = car["price_per_day"] * rental_days
        extra_fee = (
            self.YOUNG_DRIVER_FEE_PER_DAY * rental_days if client_age < 21 else 0
        )
        return base_price + extra_fee

    @staticmethod
    def _meets_category_requirements(
        car: Mapping[str, Any], client_age: int, driving_experience_years: int
    ) -> bool:
        """Apply stricter age and experience requirements to premium cars."""
        if car["category"] == "premium":
            return client_age >= 25 and driving_experience_years >= 3
        return client_age >= 18 and driving_experience_years >= 1

    @staticmethod
    def _build_option(car: Mapping[str, Any], total_price: float) -> dict[str, Any]:
        """Return the existing public response structure."""
        return {
            "model": car["model"],
            "category": car["category"],
            "total_price": total_price,
            "horsepower": car["horsepower"],
            "seats": car["seats"],
        }
