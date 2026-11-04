# Python Unit Testing — Car Rental Booking System

A Python software testing project focused on **unit testing, boundary value analysis, structural testing, code coverage, and mutation testing**.

The project uses a car rental eligibility and pricing system to demonstrate how automated tests can validate business rules, detect defects, and improve software quality.

## Testing Results

| Metric | Result |
| --- | --- |
| Automated tests | **77 passed** |
| Subtests | 76 passed |
| Statement coverage | **100%** |
| Branch coverage | **100%** (56 branches) |
| Mutants executed | 278 |
| Surviving mutants | 6 |
| Mutation non-survival rate | **97.84%** |

Mutation testing improved from **84.53% to 97.84%** after adding 10 targeted regression tests, reducing surviving mutants from **43 to 6**.

*Results measured locally using Python 3.15.2. The mutation non-survival rate is calculated from the reported survivor count.*

## What Is Tested?

The booking processor evaluates driver eligibility, vehicle availability, seating requirements, rental duration, budget constraints, and rental pricing.

The test suite demonstrates:

- **Equivalence Partitioning** — valid and invalid input classes.
- **Boundary Value Analysis** — age, experience, horsepower, and budget thresholds.
- **Structural Testing** — decisions, conditions, loops, and execution paths.
- **Input Validation** — malformed data, missing fields, and numeric edge cases.
- **Regression Testing** — preserving behavior after refactoring.
- **Mutation Testing** — measuring how effectively tests detect code changes.

The project also includes typed domain models, structured error handling, and compatibility tests for the original booking interface.

**Technologies:** Python, unittest, pytest, Coverage.py, pytest-cov, Cosmic Ray, and GitHub Actions.

## Getting Started

**Requirements:** Python 3.13+ and pip.

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd Python-Unit-Testing
python -m pip install -r requirements.txt
```

Run all tests with statement and branch coverage:

```bash
python -m pytest -v --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Alternatively, run the unittest suite:

```bash
python -m unittest discover -s tests -v
```

## Mutation Testing

Cosmic Ray introduces small modifications (*mutants*) into the booking processor to determine whether the test suite can detect them.

Mutation testing targets `src/rental_booking_processor.py`.

```bash
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
cr-report session.sqlite
```

To inspect surviving mutants:

```bash
cr-report session.sqlite --surviving-only --show-diff
```

**Final recorded result:** 278 mutants executed, 6 survived.

The six surviving mutants involve redundant seat validation (3), non-finite price handling (1), an already-enforced minimum age (1), and an internal method decorator (1).

These cases were reviewed rather than adding artificial tests solely to maximize the score. The non-finite price mutation remains a candidate for further edge-case investigation.

The results highlight why **100% code coverage does not necessarily guarantee 100% test effectiveness**.

## Continuous Integration

GitHub Actions runs the automated test suite on pushes and pull requests using Python 3.13.

The CI workflow is configured to enforce **100% combined statement and branch coverage**, helping detect regressions before changes are merged.

See [`.github/workflows/tests.yml`](.github/workflows/tests.yml).
