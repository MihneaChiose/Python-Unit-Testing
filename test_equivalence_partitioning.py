import unittest
from src.rental_booking_processor import RentalBookingProcessor


class TestEquivalencePartitioning(unittest.TestCase):

    def setUp(self):
        # aceasta metoda se executa inainte de fiecare test
        # initializam obiectul pe care il testam
        self.processor = RentalBookingProcessor()

        # definim un set standard de masini valide
        # il folosim in mai multe teste pentru a nu repeta codul
        self.cars_sample = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            },
            {
                "model": "Skoda Octavia",
                "category": "standard",
                "price_per_day": 100,
                "available": True,
                "horsepower": 110,
                "seats": 5
            },
            {
                "model": "BMW X5",
                "category": "premium",
                "price_per_day": 300,
                "available": True,
                "horsepower": 250,
                "seats": 5
            }
        ]

    def test_underage_client(self):
        # clasa de echivalenta: client_age < 18 (invalid)
        # ne asteptam la mesaj de eroare pentru client minor
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=17,
            has_license=True,
            driving_experience_years=1,
            rental_days=3,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client is underage")

    def test_client_without_license(self):
        # clasa de echivalenta: has_license = False (invalid)
        # chiar daca restul datelor sunt valide, clientul nu poate inchiria
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=False,
            driving_experience_years=5,
            rental_days=3,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client has no valid license")

    def test_negative_driving_experience(self):
        # clasa de echivalenta: driving_experience_years < 0 (invalid)
        # experienta negativa nu este acceptata
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=True,
            driving_experience_years=-1,
            rental_days=3,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "Invalid driving experience")

    def test_invalid_rental_period(self):
        # clasa de echivalenta: rental_days <= 0 (invalid)
        # perioada de inchiriere trebuie sa fie pozitiva
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=0,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "Invalid rental period")

    def test_invalid_budget(self):
        # clasa de echivalenta: budget <= 0 (invalid)
        # bugetul trebuie sa fie pozitiv
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=3,
            budget=0,
            min_seats_needed=4
        )
        self.assertEqual(result, "Invalid budget")

    def test_invalid_seat_requirement(self):
        # clasa de echivalenta: min_seats_needed <= 0 (invalid)
        # cerinta privind locurile trebuie sa fie pozitiva
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=3,
            budget=500,
            min_seats_needed=0
        )
        self.assertEqual(result, "Invalid seat requirement")

    def test_no_cars_available_empty_list(self):
        # clasa de echivalenta: cars = lista goala
        # chiar daca datele clientului sunt valide, nu exista masini disponibile
        result = self.processor.process_booking(
            cars=[],
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=3,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_valid_economy_or_standard_option_exists(self):
        # clasa de echivalenta: caz valid in care exista masini eligibile
        # clientul indeplineste conditiile pentru economy/standard
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=22,
            has_license=True,
            driving_experience_years=2,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )

        # ne asteptam sa primim o lista de masini
        self.assertIsInstance(result, list)

        # verificam ca cel putin o masina valida este returnata
        self.assertTrue(any(car["model"] == "Dacia Logan" for car in result))

    def test_premium_allowed_for_eligible_client(self):
        # clasa de echivalenta: client eligibil pentru masini premium
        # conditii: varsta >= 25 si experienta >= 3 ani
        result = self.processor.process_booking(
            cars=self.cars_sample,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=1000,
            min_seats_needed=4
        )

        # verificam ca rezultatul este lista
        self.assertIsInstance(result, list)

        # verificam ca exista cel putin o masina premium in rezultat
        self.assertTrue(any(car["category"] == "premium" for car in result))


if __name__ == "__main__":
    unittest.main()

# python -m unittest tests.test_equivalence_partitioning
# python -m unittest tests.test_boundary_values
# python -m unittest discover -s tests