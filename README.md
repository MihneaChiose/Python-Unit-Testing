# Python-Unit-Testing

This project demonstrates several software testing techniques using a simplified car rental booking system.

The main objective of the project is to implement and evaluate:

- Equivalence Partitioning
- Boundary Value Analysis
- Structural Coverage Testing
- Mutation Testing

The application logic is implemented in `RentalBookingProcessor`, which simulates the validation and processing of car rental requests based on customer age, driving experience, rental duration and preferred vehicle category.

## Running the project

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment and install the dependencies:

```bash
pip install -r requirements.txt
```

Run the unit tests:

```bash
python -m unittest discover -s tests
```

or:

```bash
pytest
```

Generate a coverage report:

```bash
coverage run -m unittest discover -s tests
coverage report -m
```

Run mutation testing:

```bash
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
```
