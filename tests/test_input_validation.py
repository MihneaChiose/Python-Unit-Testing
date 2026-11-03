"""Regression tests for malformed booking requests and vehicle data."""

import unittest
from copy import deepcopy

from src.rental_booking_processor import RentalBookingProcessor


class TestInputValidation(unittest.TestCase):
    def setUp(self):
        self.processor = RentalBookingProcessor()
        self.car = {
            "model": "Dacia Logan",
            "category": "economy",
            "price_per_day": 50,
            "available": True,
            "horsepower": 90,
            "seats": 5,
        }

    def book(self, **overrides):
        request = {
            "cars": [deepcopy(self.car)],
            "client_age": 25,
            "has_license": True,
            "driving_experience_years": 5,
            "rental_days": 2,
            "budget": 200,
            "min_seats_needed": 4,
        }
        request.update(overrides)
        return self.processor.process_booking(**request)

    def test_invalid_client_age(self):
        for value, message in [
            ("25", "Invalid client age"),
            (None, "Invalid client age"),
            (True, "Invalid client age"),
            (-1, "Client is underage"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(self.book(client_age=value), message)

    def test_invalid_license_status(self):
        for value, message in [
            ("yes", "Invalid license status"),
            (1, "Invalid license status"),
            (False, "Client has no valid license"),
        ]:
            with self.subTest(value=value):
                self.assertEqual(self.book(has_license=value), message)

    def test_invalid_driving_experience(self):
        for value in ["5", -1, True, None]:
            with self.subTest(value=value):
                self.assertEqual(
                    self.book(driving_experience_years=value),
                    "Invalid driving experience",
                )

    def test_invalid_rental_period(self):
        for value in [2.5, "2", 0, True, None]:
            with self.subTest(value=value):
                self.assertEqual(self.book(rental_days=value), "Invalid rental period")

    def test_invalid_budget(self):
        for value in ["200", None, False, float("nan"), float("inf"), float("-inf"), 0]:
            with self.subTest(value=value):
                self.assertEqual(self.book(budget=value), "Invalid budget")

    def test_invalid_seat_requirement(self):
        for value in ["4", True, 0, None, 2.5]:
            with self.subTest(value=value):
                self.assertEqual(
                    self.book(min_seats_needed=value), "Invalid seat requirement"
                )

    def test_invalid_cars_collection(self):
        for value in [None, 123, "not a list", b"abc", {"model": "car"}]:
            with self.subTest(value=value):
                self.assertEqual(self.book(cars=value), "Invalid cars collection")

    def test_skips_invalid_vehicle_fields_and_keeps_valid_car(self):
        invalid_fields = {
            "model": ["", "   ", None],
            "category": ["luxury", []],
            "price_per_day": [-5, 0, None, "50", True, float("nan"), float("inf")],
            "available": ["yes", 1, False],
            "seats": [-2, 0, "5", True],
            "horsepower": [-10, 0, "90", False],
        }
        for field, invalid_values in invalid_fields.items():
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    invalid = deepcopy(self.car)
                    invalid[field] = value
                    result = self.book(cars=[invalid, deepcopy(self.car)])
                    self.assertEqual(
                        result,
                        [
                            {
                                "model": "Dacia Logan",
                                "category": "economy",
                                "total_price": 100,
                                "horsepower": 90,
                                "seats": 5,
                            }
                        ],
                    )

    def test_skips_incomplete_and_non_mapping_cars(self):
        incomplete = deepcopy(self.car)
        del incomplete["price_per_day"]
        for value in [None, 17, "car", [], {}, incomplete]:
            with self.subTest(value=value):
                result = self.book(cars=[value, deepcopy(self.car)])
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 1)

    def test_invalid_only_vehicles_return_no_options(self):
        invalid = deepcopy(self.car)
        invalid["price_per_day"] = -100
        self.assertEqual(self.book(cars=[invalid]), "No cars available for this client")

    def test_overflowed_rental_price_is_excluded(self):
        expensive = deepcopy(self.car)
        expensive["price_per_day"] = 1e308
        self.assertEqual(
            self.book(cars=[expensive], rental_days=100, budget=1e308),
            "No cars available for this client",
        )

    def test_accepts_fractional_prices_without_mutating_car(self):
        car = deepcopy(self.car)
        car["price_per_day"] = 42.5
        before = deepcopy(car)
        result = self.book(cars=[car])
        self.assertEqual(result[0]["total_price"], 85.0)
        self.assertEqual(car, before)

    def test_accepts_generator_of_valid_vehicles(self):
        result = self.book(cars=(car for car in [deepcopy(self.car)]))
        self.assertEqual(result[0]["model"], "Dacia Logan")


if __name__ == "__main__":
    unittest.main()
