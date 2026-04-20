import unittest
from src.rental_booking_processor import RentalBookingProcessor

# python -m unittest test_structural_coverage.py
class BaseRentalBookingTest(unittest.TestCase):
    def setUp(self):
        # initializam obiectul testat
        self.processor = RentalBookingProcessor()

        # set de masini variat, folosit in mai multe teste
        # includem masini bune si masini care vor fi filtrate pe diferite motive
        self.mixed_cars = [
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
            },
            {
                "model": "Old Car",
                "category": "luxury",
                "price_per_day": 80,
                "available": True,
                "horsepower": 100,
                "seats": 4
            },
            {
                "model": "Unavailable Car",
                "category": "economy",
                "price_per_day": 40,
                "available": False,
                "horsepower": 75,
                "seats": 4
            },
            {
                "model": "Small Car",
                "category": "economy",
                "price_per_day": 45,
                "available": True,
                "horsepower": 80,
                "seats": 2
            },
            {
                "model": "Power Car",
                "category": "standard",
                "price_per_day": 90,
                "available": True,
                "horsepower": 130,
                "seats": 5
            },
            {
                # lipseste campul "horsepower"
                "model": "Broken Car",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "seats": 4
            }
        ]


class TestStatementCoverage(BaseRentalBookingTest):
    def test_statement_coverage_invalid_input_path(self):
        # acest test acopera o ramura scurta de iesire imediata
        # ne ajuta sa executam instructiunea de validare pentru client minor
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=17,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client is underage")

    def test_statement_coverage_main_processing_path(self):
        # acest test intra in bucla, trece prin mai multe filtre
        # si executa blocul principal in care se calculeaza pretul
        # si se adauga masini in lista finala
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=2,
            budget=1000,
            min_seats_needed=4
        )

        # ne asteptam sa avem optiuni valide
        self.assertIsInstance(result, list)

        # verificam ca se adauga cel putin o masina economy/standard
        self.assertTrue(any(car["model"] == "Dacia Logan" for car in result))
        self.assertTrue(any(car["model"] == "Skoda Octavia" for car in result))

        # verificam ca se poate adauga si premium pentru client eligibil
        self.assertTrue(any(car["model"] == "BMW X5" for car in result))

    def test_statement_coverage_no_available_options(self):
        # acest test parcurge fluxul complet, dar fara sa adauge nimic in lista
        # astfel acoperim si return-ul final pentru cazul fara masini eligibile
        cars = [
            {
                "model": "Tiny Car",
                "category": "economy",
                "price_per_day": 40,
                "available": True,
                "horsepower": 80,
                "seats": 2
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")


class TestDecisionCoverage(BaseRentalBookingTest):
    def test_decision_client_without_license(self):
        # acopera decizia "if not has_license" pe True
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=25,
            has_license=False,
            driving_experience_years=3,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client has no valid license")

    def test_decision_invalid_experience(self):
        # acopera decizia "if driving_experience_years < 0" pe True
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=25,
            has_license=True,
            driving_experience_years=-1,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )
        self.assertEqual(result, "Invalid driving experience")

    def test_decision_filters_inside_loop(self):
        # acest test este gandit sa treaca prin multe decizii din interiorul buclei:
        # - masina cu camp lipsa -> continue
        # - categorie invalida -> continue
        # - indisponibila -> continue
        # - locuri insuficiente -> continue
        # - masina prea puternica pentru client restrictionat -> continue
        # - masina valida -> adaugata
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )

        self.assertIsInstance(result, list)

        # Dacia Logan trebuie sa treaca
        self.assertTrue(any(car["model"] == "Dacia Logan" for car in result))

        # Power Car trebuie respinsa pentru client sub 21 ani
        self.assertFalse(any(car["model"] == "Power Car" for car in result))

        # BMW X5 este premium si prea puternica pentru client restrictionat
        self.assertFalse(any(car["model"] == "BMW X5" for car in result))

    def test_decision_budget_exceeded(self):
        # acopera decizia "if total_price > budget" pe True
        cars = [
            {
                "model": "Affordable Car",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "horsepower": 90,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=2,
            budget=100,
            min_seats_needed=4
        )

        # total = 50 * 2 + 20 * 2 = 140 > 100
        self.assertEqual(result, "No cars available for this client")

    def test_decision_premium_rejected_because_age_or_experience(self):
        # acopera decizia pentru premium:
        # car["category"] == "premium" este True
        # dar conditia interioara client_age >= 25 and experience >= 3 este False
        cars = [
            {
                "model": "BMW X5",
                "category": "premium",
                "price_per_day": 300,
                "available": True,
                "horsepower": 110,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=24,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_decision_standard_rejected_because_low_experience(self):
        # acopera ramura else pentru economy/standard
        # dar conditia client_age >= 18 and experience >= 1 este False
        cars = [
            {
                "model": "Skoda Octavia",
                "category": "standard",
                "price_per_day": 100,
                "available": True,
                "horsepower": 110,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=0,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")


class TestConditionCoverage(BaseRentalBookingTest):
    def test_condition_age_restriction_true_experience_restriction_false(self):
        # conditia compusa:
        # if client_age < 21 or driving_experience_years < 2
        # aici avem:
        # client_age < 21 -> True
        # driving_experience_years < 2 -> False
        cars = [
            {
                "model": "Car 121",
                "category": "standard",
                "price_per_day": 80,
                "available": True,
                "horsepower": 121,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )

        # masina este respinsa din cauza puterii
        self.assertEqual(result, "No cars available for this client")

    def test_condition_age_restriction_false_experience_restriction_true(self):
        # aceeasi conditie compusa, dar cu valori inverse:
        # client_age < 21 -> False
        # driving_experience_years < 2 -> True
        cars = [
            {
                "model": "Car 121",
                "category": "standard",
                "price_per_day": 80,
                "available": True,
                "horsepower": 121,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=1,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )

        self.assertEqual(result, "No cars available for this client")

    def test_condition_age_restriction_false_experience_restriction_false(self):
        # acum vrem ca ambele conditii din expresia cu OR sa fie False
        # astfel blocul de restrictie pentru horsepower nu se aplica
        cars = [
            {
                "model": "Strong Standard",
                "category": "standard",
                "price_per_day": 80,
                "available": True,
                "horsepower": 130,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )

        self.assertIsInstance(result, list)
        self.assertTrue(any(car["model"] == "Strong Standard" for car in result))

    def test_condition_premium_age_and_experience(self):
        # conditia compusa:
        # if client_age >= 25 and driving_experience_years >= 3
        # testam cazul in care prima conditie este True si a doua este False
        cars = [
            {
                "model": "BMW X5",
                "category": "premium",
                "price_per_day": 300,
                "available": True,
                "horsepower": 110,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )

        self.assertEqual(result, "No cars available for this client")

    def test_condition_standard_age_and_experience(self):
        # conditia compusa:
        # if client_age >= 18 and driving_experience_years >= 1
        # testam prima conditie True si a doua False
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

        result = self.processor.process_booking(
            cars=cars,
            client_age=18,
            has_license=True,
            driving_experience_years=0,
            rental_days=1,
            budget=100,
            min_seats_needed=4
        )

        self.assertEqual(result, "No cars available for this client")


class TestIndependentCircuits(BaseRentalBookingTest):
    def test_circuit_1_immediate_exit_underage(self):
        # circuit independent 1:
        # iesire imediata din prima validare
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=16,
            has_license=True,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client is underage")

    def test_circuit_2_immediate_exit_no_license(self):
        # circuit independent 2:
        # trece de prima validare, apoi iese la a doua
        result = self.processor.process_booking(
            cars=self.mixed_cars,
            client_age=22,
            has_license=False,
            driving_experience_years=1,
            rental_days=2,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "Client has no valid license")

    def test_circuit_3_loop_continue_missing_field(self):
        # circuit independent 3:
        # intra in bucla si iese pe continue din cauza campurilor lipsa
        cars = [
            {
                "model": "Broken Car",
                "category": "economy",
                "price_per_day": 50,
                "available": True,
                "seats": 4
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_circuit_4_loop_continue_invalid_category(self):
        # circuit independent 4:
        # masina este respinsa pentru categorie invalida
        cars = [
            {
                "model": "Luxury Car",
                "category": "luxury",
                "price_per_day": 80,
                "available": True,
                "horsepower": 100,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_circuit_5_loop_continue_unavailable(self):
        # circuit independent 5:
        # masina este respinsa pentru indisponibilitate
        cars = [
            {
                "model": "Unavailable Car",
                "category": "economy",
                "price_per_day": 40,
                "available": False,
                "horsepower": 75,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_circuit_6_loop_continue_not_enough_seats(self):
        # circuit independent 6:
        # masina este respinsa pentru numar insuficient de locuri
        cars = [
            {
                "model": "Small Car",
                "category": "economy",
                "price_per_day": 45,
                "available": True,
                "horsepower": 80,
                "seats": 2
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_circuit_7_loop_continue_restricted_driver_high_horsepower(self):
        # circuit independent 7:
        # clientul intra in restrictia de varsta/experienta
        # apoi masina este respinsa fiind prea puternica
        cars = [
            {
                "model": "Power Car",
                "category": "standard",
                "price_per_day": 90,
                "available": True,
                "horsepower": 130,
                "seats": 5
            }
        ]

        result = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=1,
            budget=200,
            min_seats_needed=4
        )
        self.assertEqual(result, "No cars available for this client")

    def test_circuit_8_valid_standard_added(self):
        # circuit independent 8:
        # flux complet pana la append pentru economy/standard
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

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=2,
            rental_days=2,
            budget=300,
            min_seats_needed=4
        )

        self.assertIsInstance(result, list)
        self.assertTrue(any(car["model"] == "Dacia Logan" for car in result))

    def test_circuit_9_valid_premium_added(self):
        # circuit independent 9:
        # flux complet pana la append pentru premium
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

        result = self.processor.process_booking(
            cars=cars,
            client_age=25,
            has_license=True,
            driving_experience_years=3,
            rental_days=1,
            budget=500,
            min_seats_needed=4
        )

        self.assertIsInstance(result, list)
        self.assertTrue(any(car["model"] == "BMW X5" for car in result))

    def test_circuit_10_budget_continue_then_final_no_options(self):
        # circuit independent 10:
        # fluxul intra pana la calculul pretului, dar iese pe buget
        # si la final nu se adauga nimic
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

        result = self.processor.process_booking(
            cars=cars,
            client_age=20,
            has_license=True,
            driving_experience_years=2,
            rental_days=2,
            budget=100,
            min_seats_needed=4
        )

        self.assertEqual(result, "No cars available for this client")


if __name__ == "__main__":
    unittest.main()