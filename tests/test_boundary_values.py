import unittest
from src.rental_booking_processor import RentalBookingProcessor


class TestBoundaryValueAnalysis(unittest.TestCase):

    def setUp(self):
        # initializam procesorul folosit in toate testele
        self.processor = RentalBookingProcessor()

    def test_client_age_boundary_17_18(self):
        # o masina simpla, eligibila, folosita ca sa izolam testul pe varsta
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # 17 ani -> client minor
        result_17 = self.processor.process_booking(
            cars=cars,
            client_age=17,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result_17, "Client is underage")

        # 18 ani -> client valid, poate inchiria economy/standard daca restul conditiilor sunt bune
        result_18 = self.processor.process_booking(
            cars=cars,
            client_age=18,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertIsInstance(result_18, list)

    def test_client_age_boundary_20_21_extra_fee(self):
        # testam pragul 21, unde dispare taxa extra pentru soferii tineri
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # pentru 2 zile:
        # la 20 ani: 50 * 2 + 20 * 2 = 140
        # la 21 ani: 50 * 2 = 100

        # bugetul 100 nu ajunge pentru client de 20 ani
        result_20 = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=100,
            min_seats_needed=4
        )
        self.assertEqual(result_20, "No cars available for this client")

        # acelasi buget ajunge pentru client de 21 ani
        result_21 = self.processor.process_booking(
            cars=cars,
            client_age=21,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=100,
            min_seats_needed=4
        )
        self.assertIsInstance(result_21, list)

    def test_client_age_boundary_24_25_for_premium(self):
        # testam pragul 25, necesar pentru masini premium
        cars = [
            {
                "model": "BMW X5",
                "category": "premium",
                "price_per_day": 300,
                "available": True,
                "horsepower": 250,
                "seats": 5
            }
        ]

        # 24 ani -> premium nu este permis
        result_24 = self.processor.process_booking(
            cars=cars,
            client_age=24,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result_24, "No cars available for this client")

        # 25 ani -> premium este permis daca experienta este suficienta
        result_25 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )
        self.assertIsInstance(result_25, list)
        self.assertTrue(any(car["category"] == "premium" for car in result_25))

    def test_driving_experience_boundary_minus1_0(self):
        # testam pragul dintre experienta invalida si experienta valida ca input
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # -1 -> invalid
        result_minus1 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=-1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result_minus1, "Invalid driving experience")

        # 0 -> valid ca input, dar insuficient pentru economy/standard
        result_0 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=0,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result_0, "No cars available for this client")

    def test_driving_experience_boundary_0_1(self):
        # pragul 1 an este minimul pentru economy/standard
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # 0 ani -> nu poate inchiria economy/standard
        result_0 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=0,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result_0, "No cars available for this client")

        # 1 an -> poate inchiria economy/standard
        result_1 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertIsInstance(result_1, list)

    def test_driving_experience_boundary_2_3_for_premium(self):
        # testam pragul 3 ani pentru premium
        cars = [
            {
                "model": "BMW X5",
                "category": "premium",
                "price_per_day": 300,
                "available": True,
                "horsepower": 250,
                "seats": 5
            }
        ]

        # 2 ani -> insuficient pentru premium
        result_2 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result_2, "No cars available for this client")

        # 3 ani -> suficient pentru premium
        result_3 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )
        self.assertIsInstance(result_3, list)

    def test_rental_days_boundary_0_1(self):
        # pragul minim valid pentru rental_days este 1
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        result_0 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=0,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result_0, "Invalid rental period")

        result_1 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertIsInstance(result_1, list)

    def test_budget_boundary_under_exact_over_for_young_driver(self):
        # testam bugetul fata de un pret total exact
        # client sub 21 ani -> taxa extra se aplica
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # total = 50 * 2 + 20 * 2 = 140
        result_139 = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=139,
            min_seats_needed=4
        )
        self.assertEqual(result_139, "No cars available for this client")

        result_140 = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=140,
            min_seats_needed=4
        )
        self.assertIsInstance(result_140, list)

        result_141 = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=141,
            min_seats_needed=4
        )
        self.assertIsInstance(result_141, list)

    def test_min_seats_needed_boundary_0_1_5_6(self):
        # testam frontierele pentru numarul minim de locuri
        cars = [
            {
                "model": "Dacia Logan",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        # 0 -> invalid
        result_0 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=0
        )
        self.assertEqual(result_0, "Invalid seat requirement")

        # 1 -> valid
        result_1 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=1
        )
        self.assertIsInstance(result_1, list)

        # 5 -> exact numarul de locuri al masinii
        result_5 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=5
        )
        self.assertIsInstance(result_5, list)

        # 6 -> prea multe locuri cerute
        result_6 = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=6
        )
        self.assertEqual(result_6, "No cars available for this client")

    def test_horsepower_boundary_120_121_for_restricted_driver(self):
        # testam pragul 120 CP pentru clientii tineri sau fara experienta suficienta
        cars = [
            {
                "model": "Car 120",
                "category": "standard",
                "price_per_day": 80,
                "available": True,
                "horsepower": 120,
                "seats": 5
            },
            {
                "model": "Car 121",
                "category": "standard",
                "price_per_day": 80,
                "available": True,
                "horsepower": 121,
                "seats": 5
            }
        ]

        # clientul este restrictionat fiindca are sub 21 ani
        result = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )

        self.assertIsInstance(result, list)
        self.assertTrue(any(car["model"] == "Car 120" for car in result))
        self.assertFalse(any(car["model"] == "Car 121" for car in result))


if __name__ == "__main__":
    unittest.main()