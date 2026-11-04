# Python Unit Testing — Car Rental Booking System

A Python software testing project that demonstrates **unit testing, boundary value analysis, structural testing, code coverage, and mutation testing** using a car rental eligibility and pricing system.

The goal is to evaluate **test effectiveness and software quality**, not to build a full car rental application.

## Testing Results

| Metric | Result |
| --- | --- |
| Automated tests | **77 passed** |
| Subtests | 76 passed |
| Statement coverage | **100%** |
| Mutants executed | 278 |
| Mutants survived | **6** |
| Mutation non-survival rate | **97.84%** |

The mutation non-survival rate improved from **84.53% to 97.84%** after adding 10 targeted regression tests, reducing surviving mutants from **43 to 6**.

## What Is Tested?

The booking processor validates driver eligibility, rental duration, vehicle availability, seating requirements, budget constraints, and rental pricing.

The test suite covers:

- **Equivalence Partitioning** — valid and invalid input classes.
- **Boundary Value Analysis** — age, experience, horsepower, and budget thresholds.
- **Structural Testing** — decisions, conditions, loops, and execution paths.
- **Input Validation** — malformed data, missing fields, and numeric edge cases.
- **Mutation Testing** — detecting changes to operators, conditions, and control flow.
- **Regression Testing** — protecting existing behavior after refactoring.

The project uses `unittest`, `pytest`, `pytest-cov`, Coverage.py, and Cosmic Ray.

## Getting Started

**Requirements:** Python 3.13+ and pip.

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd Python-Unit-Testing
python -m pip install -r requirements.txt
```

Run all tests with coverage:

```bash
python -m pytest -v --cov=src --cov-report=term-missing --cov-fail-under=100
```

Run the tests using `unittest`:

```bash
python -m unittest discover -s tests -v
```

## Mutation Testing

Cosmic Ray introduces small code changes (*mutants*) to check whether the tests detect them.

The mutation target is `src/rental_booking_processor.py`.

```bash
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
cr-report session.sqlite
```

**Results:** 278 mutants executed, 6 survived.

The remaining mutants involve redundant seat validation (3), non-finite price handling (1), an already-enforced minimum age (1), and removal of an internal `@classmethod` decorator (1).

Most do not change the observable booking behavior for valid public requests. The price-handling mutant warrants further edge-case investigation, while the decorator mutation can affect direct calls to the internal method.

The results demonstrate why **100% statement coverage does not necessarily mean 100% test effectiveness**.

## Continuous Integration

GitHub Actions automatically runs the test suite on pushes and pull requests, using Python 3.13 and enforcing **100% statement coverage**.

See [`.github/workflows/tests.yml`](.github/workflows/tests.yml).
