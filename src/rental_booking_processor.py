"""Business rules for evaluating car rental requests."""

from collections.abc import Iterable
from typing import Any


class RentalBookingProcessor:
    """Select eligible cars and calculate their rental prices."""

    REQUIRED_CAR_FIELDS = frozenset(
        {"model", "category", "price_per_day", "available", "horsepower", "seats"}
    )
    VALID_CATEGORIES = frozenset({"economy", "standard", "premium"})
    YOUNG_DRIVER_FEE_PER_DAY = 20
    RESTRICTED_DRIVER_MAX_HORSEPOWER = 120

    def process_booking(
        self,
        cars: Iterable[dict[str, Any]],
        client_age: int,
        has_license: bool,
        driving_experience_years: int,
        rental_days: int,
        budget: float,
        min_seats_needed: int,
    ) -> list[dict[str, Any]] | str:
        """Return eligible cars with prices, or a validation/status message.

        The result format is retained for compatibility with existing callers.
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

        available_options: list[dict[str, Any]] = []
        for car in cars:
            if not self._passes_vehicle_filters(
                car, client_age, driving_experience_years, min_seats_needed
            ):
                continue

            total_price = self._calculate_total_price(car, client_age, rental_days)
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

    @staticmethod
    def _validate_request(
        client_age: int,
        has_license: bool,
        driving_experience_years: int,
        rental_days: int,
        budget: float,
        min_seats_needed: int,
    ) -> str | None:
        """Check request values in the original validation order."""
        if client_age < 18:
            return "Client is underage"
        if not has_license:
            return "Client has no valid license"
        if driving_experience_years < 0:
            return "Invalid driving experience"
        if rental_days <= 0:
            return "Invalid rental period"
        if budget <= 0:
            return "Invalid budget"
        if min_seats_needed <= 0:
            return "Invalid seat requirement"
        return None

    def _passes_vehicle_filters(
        self,
        car: dict[str, Any],
        client_age: int,
        driving_experience_years: int,
        min_seats_needed: int,
    ) -> bool:
        """Check vehicle data, availability, seats and horsepower restrictions."""
        if not self.REQUIRED_CAR_FIELDS.issubset(car):
            return False
        if car["category"] not in self.VALID_CATEGORIES:
            return False
        if not car["available"]:
            return False
        if car["seats"] < min_seats_needed:
            return False
        return not (
            (client_age < 21 or driving_experience_years < 2)
            and car["horsepower"] > self.RESTRICTED_DRIVER_MAX_HORSEPOWER
        )

    def _calculate_total_price(
        self, car: dict[str, Any], client_age: int, rental_days: int
    ) -> float:
        """Calculate the total amount, including the young-driver surcharge."""
        base_price = car["price_per_day"] * rental_days
        extra_fee = (
            self.YOUNG_DRIVER_FEE_PER_DAY * rental_days if client_age < 21 else 0
        )
        return base_price + extra_fee

    @staticmethod
    def _meets_category_requirements(
        car: dict[str, Any], client_age: int, driving_experience_years: int
    ) -> bool:
        """Apply stricter age and experience requirements to premium cars."""
        if car["category"] == "premium":
            return client_age >= 25 and driving_experience_years >= 3
        return client_age >= 18 and driving_experience_years >= 1

    @staticmethod
    def _build_option(car: dict[str, Any], total_price: float) -> dict[str, Any]:
        """Return the established public response structure."""
        return {
            "model": car["model"],
            "category": car["category"],
            "total_price": total_price,
            "horsepower": car["horsepower"],
            "seats": car["seats"],
        }
