class RentalBookingProcessor:
    # proceseaza cererea unui client
    def process_booking(
        self,
        cars,
        client_age,
        has_license,
        driving_experience_years,
        rental_days,
        budget,
        min_seats_needed
    ):
        # validari de baza
        if client_age < 18:
            return "Client is underage"

        if not has_license:
            return "Client has no valid license"

        if driving_experience_years < 0:
            return "Invalid driving experience"

        if rental_days <= 0:
            return "Invalid rental period"

        if budget <= 0:
            return "Invalid budget"

        if min_seats_needed <= 0:
            return "Invalid seat requirement"

        valid_categories = ["economy", "standard", "premium"]
        available_options = []

        # parcurgem toate masinile
        for car in cars:
            # masina trebuie sa aiba toate campurile necesare
            if (
                "model" not in car
                or "category" not in car
                or "price_per_day" not in car
                or "available" not in car
                or "horsepower" not in car
                or "seats" not in car
            ):
                continue

            # categoria trebuie sa fie valida
            if car["category"] not in valid_categories:
                continue

            # masina trebuie sa fie disponibila
            if not car["available"]:
                continue

            # masina trebuie sa aiba suficiente locuri
            if car["seats"] < min_seats_needed:
                continue

            # soferii tineri sau fara experienta nu pot lua masini puternice
            if client_age < 21 or driving_experience_years < 2:
                if car["horsepower"] > 120:
                    continue

            base_price = car["price_per_day"] * rental_days
            extra_fee = 0

            # soferii sub 21 de ani platesc taxa extra
            if client_age < 21:
                extra_fee = 20 * rental_days

            total_price = base_price + extra_fee

            # daca pretul depaseste bugetul, trecem peste masina
            if total_price > budget:
                continue

            # masinile premium cer varsta si experienta mai mare
            if car["category"] == "premium":
                if client_age >= 25 and driving_experience_years >= 3:
                    available_options.append(
                        {
                            "model": car["model"],
                            "category": car["category"],
                            "total_price": total_price,
                            "horsepower": car["horsepower"],
                            "seats": car["seats"]
                        }
                    )
            else:
                # economy si standard pot fi inchiriate mai usor
                if client_age >= 18 and driving_experience_years >= 1:
                    available_options.append(
                        {
                            "model": car["model"],
                            "category": car["category"],
                            "total_price": total_price,
                            "horsepower": car["horsepower"],
                            "seats": car["seats"]
                        }
                    )

        # daca nu exista masini eligibile
        if len(available_options) == 0:
            return "No cars available for this client"

        return available_options