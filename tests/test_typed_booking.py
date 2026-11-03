"""Tests for the new typed booking interface and legacy compatibility."""

import unittest
from dataclasses import FrozenInstanceError, replace
from unittest.mock import patch

from src.models import (
    BookingError,
    BookingErrorCode,
    BookingOption,
    BookingRequest,
    BookingResult,
    Car,
)
from src.rental_booking_processor import RentalBookingProcessor


class TestTypedBooking(unittest.TestCase):
    def setUp(self):
        self.processor = RentalBookingProcessor()
        self.car = Car(
            model="Dacia Logan",
            category="economy",
            price_per_day=50,
            available=True,
            horsepower=90,
            seats=5,
        )
        self.request = BookingRequest(
            cars=(self.car,),
            client_age=25,
            has_license=True,
            driving_experience_years=5,
            rental_days=2,
            budget=200,
            min_seats_needed=4,
        )

    def test_typed_success_matches_legacy_result(self):
        result = self.processor.evaluate_booking(self.request)
        legacy = self.processor.process_booking(
            cars=[self.car.to_mapping()],
            client_age=25,
            has_license=True,
            driving_experience_years=5,
            rental_days=2,
            budget=200,
            min_seats_needed=4,
        )
        self.assertTrue(result.success)
        self.assertIsNone(result.error)
        self.assertEqual(
            result.options,
            (BookingOption("Dacia Logan", "economy", 100, 90, 5),),
        )
        self.assertEqual(
            [
                {
                    "model": option.model,
                    "category": option.category,
                    "total_price": option.total_price,
                    "horsepower": option.horsepower,
                    "seats": option.seats,
                }
                for option in result.options
            ],
            legacy,
        )

    def test_validation_errors_have_stable_codes(self):
        cases = [
            (
                "client_age",
                "25",
                BookingErrorCode.INVALID_CLIENT_AGE,
                "Invalid client age",
            ),
            ("client_age", 17, BookingErrorCode.UNDERAGE, "Client is underage"),
            (
                "has_license",
                "yes",
                BookingErrorCode.INVALID_LICENSE_STATUS,
                "Invalid license status",
            ),
            (
                "has_license",
                False,
                BookingErrorCode.NO_LICENSE,
                "Client has no valid license",
            ),
            (
                "driving_experience_years",
                -1,
                BookingErrorCode.INVALID_DRIVING_EXPERIENCE,
                "Invalid driving experience",
            ),
            (
                "rental_days",
                0,
                BookingErrorCode.INVALID_RENTAL_PERIOD,
                "Invalid rental period",
            ),
            ("budget", -1, BookingErrorCode.INVALID_BUDGET, "Invalid budget"),
            (
                "min_seats_needed",
                0,
                BookingErrorCode.INVALID_SEAT_REQUIREMENT,
                "Invalid seat requirement",
            ),
        ]
        for name, value, code, message in cases:
            with self.subTest(field=name, value=value):
                result = self.processor.evaluate_booking(
                    replace(self.request, **{name: value})
                )
                self.assertFalse(result.success)
                self.assertEqual(result.options, ())
                self.assertEqual(result.error, BookingError(code, message))

    def test_no_eligible_cars_is_a_structured_error(self):
        request = replace(self.request, cars=())
        result = self.processor.evaluate_booking(request)
        self.assertFalse(result.success)
        assert result.error is not None
        self.assertEqual(result.error.code, BookingErrorCode.NO_ELIGIBLE_CARS)
        self.assertEqual(result.error.message, "No cars available for this client")

    def test_invalid_vehicle_is_skipped_in_typed_api(self):
        bad_car = replace(self.car, price_per_day=-20)
        request = replace(self.request, cars=(bad_car, self.car))
        result = self.processor.evaluate_booking(request)
        self.assertTrue(result.success)
        self.assertEqual(len(result.options), 1)
        self.assertEqual(result.options[0].model, "Dacia Logan")

    def test_unknown_message_is_preserved(self):
        with patch.object(self.processor, "process_booking", return_value="Unexpected"):
            result = self.processor.evaluate_booking(self.request)
        self.assertFalse(result.success)
        assert result.error is not None
        self.assertEqual(result.error.code, BookingErrorCode.UNKNOWN)
        self.assertEqual(result.error.message, "Unexpected")

    def test_models_are_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            self.car.seats = 10

    def test_result_cannot_be_empty_or_both_success_and_error(self):
        with self.assertRaises(ValueError):
            BookingResult(options=())
        with self.assertRaises(ValueError):
            BookingResult(
                options=(BookingOption("Dacia Logan", "economy", 100, 90, 5),),
                error=BookingError(BookingErrorCode.INVALID_BUDGET, "Invalid budget"),
            )


if __name__ == "__main__":
    unittest.main()
