"""Regression tests for the public booking result contract."""

import unittest
from copy import deepcopy

from src.rental_booking_processor import RentalBookingProcessor


class TestBookingContract(unittest.TestCase):
    def setUp(self):
        self.processor = RentalBookingProcessor()
        self.cars = [
            {
                "model": "Skoda Octavia",
                "category": "standard",
                "price_per_day": 60,
                "available": True,
                "horsepower": 110,
                "seats": 5,
            },
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5,
            },
        ]

    def test_response_fields_prices_and_input_order(self):
        result = self.processor.process_booking(
            cars=self.cars,
            client_age=20,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4,
        )
        self.assertEqual(
            result,
            [
                {
                    "model": "Skoda Octavia",
                    "category": "standard",
                    "total_price": 160,
                    "horsepower": 110,
                    "seats": 5,
                },
                {
                    "model": "Dacia Logan",
                    "category": "economy",
                    "total_price": 140,
                    "horsepower": 90,
                    "seats": 5,
                },
            ],
        )

    def test_processing_does_not_mutate_input_vehicles(self):
        original_cars = deepcopy(self.cars)
        self.processor.process_booking(
            cars=self.cars,
            client_age=25,
            has_license=True,
            driving_experience_years=5,
            rental_days=1,
            budget=200,
            min_seats_needed=4,
        )
        self.assertEqual(self.cars, original_cars)


if __name__ == "__main__":
    unittest.main()
