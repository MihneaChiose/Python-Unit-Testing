"""Regression tests targeting mutations identified by Cosmic Ray."""

import unittest
from typing import Any, get_type_hints

from src.rental_booking_processor import RentalBookingProcessor


class TestMutationRegressions(unittest.TestCase):
    def setUp(self):
        self.processor = RentalBookingProcessor()

    @staticmethod
    def car(**overrides):
        vehicle = {
            "model": "Valid car",
            "category": "economy",
            "price_per_day": 10,
            "available": True,
            "horsepower": 90,
            "seats": 5,
        }
        vehicle.update(overrides)
        return vehicle

    def book(self, cars, **overrides):
        request = {
            "cars": cars,
            "client_age": 25,
            "has_license": True,
            "driving_experience_years": 5,
            "rental_days": 1,
            "budget": 1000,
            "min_seats_needed": 1,
        }
        request.update(overrides)
        return self.processor.process_booking(**request)

    def assert_selected(self, result, expected_models):
        self.assertIsInstance(result, list)
        self.assertEqual(
            [car["model"] for car in result],
            expected_models,
        )

    def test_premium_category_uses_value_equality(self):
        dynamically_created_category = bytearray(b"premium").decode("ascii")

        self.assertEqual(dynamically_created_category, "premium")
        self.assertIsNot(dynamically_created_category, "premium")

        result = self.book(
            [self.car(category=dynamically_created_category)],
            client_age=22,
            driving_experience_years=2,
        )

        self.assertEqual(
            result,
            "No cars available for this client",
        )

    def test_high_horsepower_allowed_at_exact_restriction_boundaries(self):
        for age, experience in [(21, 5), (25, 2)]:
            with self.subTest(age=age, experience=experience):
                result = self.book(
                    [self.car(horsepower=121)],
                    client_age=age,
                    driving_experience_years=experience,
                )
                self.assert_selected(result, ["Valid car"])

    def test_negative_request_limits_are_rejected(self):
        for field, message in [
            ("rental_days", "Invalid rental period"),
            ("min_seats_needed", "Invalid seat requirement"),
        ]:
            with self.subTest(field=field):
                result = self.book(
                    [self.car()],
                    **{field: -1},
                )
                self.assertEqual(result, message)

    def test_premium_allowed_above_age_and_experience_thresholds(self):
        result = self.book(
            [self.car(category="premium", horsepower=180)],
            client_age=26,
            driving_experience_years=4,
        )
        self.assert_selected(result, ["Valid car"])

    def test_overflowed_price_does_not_stop_processing_next_car(self):
        result = self.book(
            [
                self.car(model="Overflow", price_per_day=1e308),
                self.car(model="Affordable"),
            ],
            rental_days=100,
            budget=1e308,
        )
        self.assert_selected(result, ["Affordable"])

    def test_over_budget_car_does_not_stop_processing_next_car(self):
        result = self.book(
            [
                self.car(model="Too expensive", price_per_day=150),
                self.car(model="Affordable"),
            ],
            budget=100,
        )
        self.assert_selected(result, ["Affordable"])

    def test_ineligible_premium_does_not_stop_processing_next_car(self):
        result = self.book(
            [
                self.car(model="Premium", category="premium"),
                self.car(model="Economy"),
            ],
            client_age=22,
            driving_experience_years=2,
        )
        self.assert_selected(result, ["Economy"])

    def test_small_positive_prices_and_budget_are_accepted(self):
        result = self.book(
            [self.car(price_per_day=0.25)],
            budget=0.75,
        )
        self.assert_selected(result, ["Valid car"])
        self.assertEqual(result[0]["total_price"], 0.25)

    def test_single_seat_and_one_horsepower_are_valid(self):
        for field in ("seats", "horsepower"):
            with self.subTest(field=field):
                result = self.book([self.car(**{field: 1})])
                self.assert_selected(result, ["Valid car"])

    def test_return_annotations_can_be_resolved(self):
        self.assertEqual(
            get_type_hints(RentalBookingProcessor.process_booking)["return"],
            list[dict[str, Any]] | str,
        )
        self.assertEqual(
            get_type_hints(RentalBookingProcessor._validate_request)["return"],
            str | None,
        )


if __name__ == "__main__":
    unittest.main()
