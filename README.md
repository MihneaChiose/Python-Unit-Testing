
# Car Rental Booking — Python Business Logic & Automated Testing

A small Python project that evaluates **car rental eligibility and pricing** based on driver details, rental requirements, and available vehicles. Developed as a collaborative university project, it demonstrates how business rules can be implemented and verified using automated tests.

> **Project scope:** This is a Python business-logic module, not yet a web application or a booking platform. It does not expose an API or store reservations in a database.

## Highlights

- Filters a list of vehicles against driver eligibility, seat requirements, availability, and budget.
- Calculates rental costs, including an additional daily fee for drivers under 21.
- Includes **45 automated tests** covering input classes, boundary conditions, and structural paths.
- Uses **pytest / unittest**, **Coverage.py**, and **Cosmic Ray** for test execution and quality analysis.
- Runs tests and checks source-code statement coverage automatically in **GitHub Actions** (once the included workflow is pushed to GitHub).

## Business rules

The main method is `RentalBookingProcessor.process_booking(...)` in `src/rental_booking_processor.py`.

| Area | Current behavior |
| --- | --- |
| Driver age | Must be at least 18. |
| Driver's license | Must be valid (`has_license=True`). |
| Driving experience | Cannot be negative; at least 1 year is required to receive an economy or standard car. |
| Premium cars | Require an age of at least 25 and at least 3 years of driving experience. |
| Powerful cars | Drivers younger than 21 **or** with fewer than 2 years of experience cannot rent cars exceeding 120 horsepower. |
| Young-driver fee | Drivers younger than 21 pay an additional 20 units per rental day. |
| Rental constraints | The number of days, budget, and minimum seat requirement must be positive; each selected car must be available, have enough seats, and fit within the total budget. |
| Vehicle data | Vehicles missing required fields or using an unsupported category are skipped. |

The method returns a **list of eligible vehicles with calculated total prices**, or a **descriptive string** when validation fails or no cars qualify. Monetary values are represented as numbers without a specified currency.

## Example

The example below uses the existing Python module directly, without additional dependencies or a web server:

```python
from src.rental_booking_processor import RentalBookingProcessor

cars = [
    {"model": "Dacia Logan", "category": "economy", "price_per_day": 50,
     "available": True, "horsepower": 90, "seats": 5},
    {"model": "Skoda Octavia", "category": "standard", "price_per_day": 100,
     "available": True, "horsepower": 110, "seats": 5},
    {"model": "BMW X5", "category": "premium", "price_per_day": 300,
     "available": True, "horsepower": 250, "seats": 5},
]

result = RentalBookingProcessor().process_booking(
    cars=cars,
    client_age=25,
    has_license=True,
    driving_experience_years=5,
    rental_days=2,
    budget=300,
    min_seats_needed=4,
)

for car in result:
    print(f"{car['model']}: {car['total_price']}")
```

Expected output:

```text
Dacia Logan: 100
Skoda Octavia: 200
```

The BMW is excluded because its two-day rental price exceeds the specified budget.

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── tests.yml                 # Continuous integration
├── src/
│   └── rental_booking_processor.py   # Rental eligibility and pricing rules
├── tests/
│   ├── test_equivalence_partitioning.py
│   ├── test_boundary_values.py
│   ├── test_structural_coverage.py
│   └── test_mutation_additional.py
├── media/                            # Flowchart, CFG, and project presentation
├── cosmic-ray.toml                   # Mutation testing configuration
└── requirements.txt
```

## Getting started

**Requirements:** Python 3.13 or newer is recommended for the setup used in this project, and Git if you are cloning the repository. The project was also successfully run locally with Python 3.15.2 on Windows.

1. Open a terminal in the repository root and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate the environment:

   **Windows PowerShell**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**

   ```bash
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Execute all tests:

   ```bash
   python -m pytest -v
   ```

   Alternatively, execute the same `unittest` tests using Python's standard library:

   ```bash
   python -m unittest discover -s tests -v
   ```

## Testing strategy and measured results

| Technique | Test suite | What it checks |
| --- | --- | --- |
| Equivalence partitioning | `test_equivalence_partitioning.py` | Representative valid and invalid inputs. |
| Boundary value analysis | `test_boundary_values.py` | Eligibility and pricing thresholds (e.g., 18, 21, 25 years). |
| Structural testing | `test_structural_coverage.py` | Statements, decisions, conditions, and independent execution paths. |
| Mutation-focused regression tests | `test_mutation_additional.py` | Selected mutations involving loop control. |

**Observed local baseline (November 2026):**

| Measurement | Result |
| --- | --- |
| Tests | **45 / 45 passed** |
| Statement coverage of `src/rental_booking_processor.py` | **100%** (43 statements, 0 missed) |
| Overall statement coverage including test files | **99%** in the local report |
| Mutation testing with Cosmic Ray | **171 killed / 191 generated**, **20 survived** (~89.53% killed) |

These are recorded local results, not a claim that all possible defects have been detected. Statement coverage is different from branch coverage, and surviving mutants should be reviewed individually.

Generate a source-focused coverage report:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

For an HTML coverage report:

```bash
python -m pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html`.

### Mutation testing

Cosmic Ray is configured to mutate `src/rental_booking_processor.py` and execute the existing unit tests.

```bash
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
cr-report session.sqlite
```

Use a new session filename (or remove the previous session file) before reinitializing. `session.sqlite` is excluded from Git by `.gitignore`.

## Continuous integration

The workflow at [`.github/workflows/tests.yml`](.github/workflows/tests.yml) is configured to run on **push** and **pull request**. It installs dependencies, runs pytest, reports source-code statement coverage, and fails if coverage of `src` falls below 100%.

This workflow uses **Python 3.13 on Ubuntu**. Check the repository's **Actions** tab for the actual execution status after publishing the workflow; a locally present workflow alone does not mean CI has run successfully.

Mutation testing remains a **separate, manually triggered local check** for now because it is more expensive than regular unit tests.

## Diagrams and demo material

- [Booking workflow diagram](media/Flowchart%20process_booking.png)
- [Control-flow graph (CFG)](media/CFG.png)
- [Mutation testing demonstration](media/Mutations%20Demo.mp4)
- [University project presentation](media/Prezentare.pptx)

## Roadmap

The current repository intentionally focuses on tested business logic. Potential next steps to evolve it into a software/backend portfolio project:

- Refactor validation, vehicle filtering, and price calculation into smaller, type-annotated components.
- Define consistent domain models and error handling; add tests for malformed vehicle data.
- Introduce a **FastAPI** REST API with request/response validation and integration tests.
- Add **PostgreSQL** persistence for vehicles and bookings, using an ORM and schema migrations.
- Review surviving Cosmic Ray mutants and document the resulting test improvements.

## Project context and attribution

This project was created collaboratively for a university assignment. The implementation and tests are presented as a learning project, with further improvements planned for portfolio use. Individual contributions should be described accurately by each collaborator when referencing the project in a CV.
