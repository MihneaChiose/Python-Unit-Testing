import unittest
from src.rental_booking_processor import RentalBookingProcessor


class TestRentalBookingProcessorMutationAdditional(unittest.TestCase):

    def setUp(self):
        # cream obiectul care va fi testat
        self.processor = RentalBookingProcessor()

    def test_kills_replace_continue_with_break_for_unavailable_car(self):
        # acest test este gandit pentru un mutant de tip:
        # if not car["available"]:
        #     continue
        #
        # devenit:
        # if not car["available"]:
        #     break
        #
        # ideea testului:
        # - prima masina este indisponibila
        # - a doua masina este valida
        #
        # in programul original:
        # - prima masina este sarita
        # - a doua masina este analizata si acceptata
        #
        # in mutant:
        # - la prima masina se executa break
        # - bucla se opreste si a doua masina nu mai este analizata
        cars = [
            {
                "model": "Opel Corsa",
                "category": "economy",
                "price_per_day": 30,
                "available": False,
                "horsepower": 90,
                "seats": 4
            },
            {
                "model": "Renault Clio",
                "category": "economy",
                "price_per_day": 35,
                "available": True,
                "horsepower": 100,
                "seats": 4
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=2,
            budget=100,
            min_seats_needed=4
        )

        # in varianta corecta a programului, a doua masina trebuie gasita
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["model"], "Renault Clio")
        self.assertEqual(result[0]["total_price"], 70)

    def test_kills_replace_continue_with_break_for_not_enough_seats(self):
        # acest test este gandit pentru un mutant de tip:
        # if car["seats"] < min_seats_needed:
        #     continue
        #
        # devenit:
        # if car["seats"] < min_seats_needed:
        #     break
        #
        # ideea testului:
        # - prima masina nu are suficiente locuri
        # - a doua masina respecta cerinta
        #
        # in programul original:
        # - prima masina este sarita
        # - a doua este acceptata
        #
        # in mutant:
        # - la prima masina se executa break
        # - bucla se opreste si a doua masina nu mai este verificata
        cars = [
            {
                "model": "Fiat 500",
                "category": "economy",
                "price_per_day": 25,
                "available": True,
                "horsepower": 70,
                "seats": 2
            },
            {
                "model": "Skoda Octavia",
                "category": "standard",
                "price_per_day": 45,
                "available": True,
                "horsepower": 110,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=30,
            has_license=True,
            driving_experience_years=5,
            rental_days=2,
            budget=120,
            min_seats_needed=4
        )

        # in varianta corecta trebuie acceptata a doua masina
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["model"], "Skoda Octavia")
        self.assertEqual(result[0]["total_price"], 90)


if __name__ == "__main__":
    unittest.main()