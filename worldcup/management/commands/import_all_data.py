import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from worldcup.models import Continent, Country, City, WorldCup, Game


DATA_DIR = Path("data")


def clean(value):
    if value is None:
        return ""
    return value.strip()


def get_country_by_name(name):
    return Country.objects.get(name=clean(name))


class Command(BaseCommand):
    help = "Import all World Cup CSV files"

    def handle(self, *args, **kwargs):
        self.import_continents()
        self.import_countries()
        self.import_cities()
        self.import_world_cups()
        self.import_games()

        self.stdout.write(self.style.SUCCESS("All data imported successfully"))

    def import_continents(self):
        with open(DATA_DIR / "continent.csv", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                Continent.objects.update_or_create(
                    id=int(clean(row["id"])),
                    defaults={
                        "name": clean(row["continent"]),
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} continents"))

    def import_countries(self):
        with open(DATA_DIR / "country.csv", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                continent = Continent.objects.get(name=clean(row["continent"]))

                Country.objects.update_or_create(
                    id=int(clean(row["id"])),
                    defaults={
                        "name": clean(row["country"]),
                        "continent": continent,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} countries"))

    def import_cities(self):
        with open(DATA_DIR / "city.csv", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                country = get_country_by_name(row["country"])

                City.objects.update_or_create(
                    id=int(clean(row["id"])),
                    defaults={
                        "name": clean(row["city"]),
                        "country": country,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} cities"))

    def import_world_cups(self):
        with open(DATA_DIR / "world_cup.csv", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                home_country = get_country_by_name(row["home_country"])

                home_country_second = None
                if clean(row["home_country_second"]):
                    home_country_second = get_country_by_name(row["home_country_second"])

                home_country_third = None
                if clean(row["home_country_third"]):
                    home_country_third = get_country_by_name(row["home_country_third"])

                winner = None
                if clean(row["winner"]):
                    winner = get_country_by_name(row["winner"])

                WorldCup.objects.update_or_create(
                    year=int(clean(row["year"])),
                    defaults={
                        "home_country": home_country,
                        "home_country_second": home_country_second,
                        "home_country_third": home_country_third,
                        "winner": winner,
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} world cups"))
    def import_games(self):
        with open(DATA_DIR / "game.csv", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            count = 0
            for row in reader:
                country_1 = get_country_by_name(row["name_country_1"])
                country_2 = get_country_by_name(row["name_country_2"])
                home_country = get_country_by_name(row["home_country"])
                world_cup = WorldCup.objects.get(year=int(clean(row["world_cup"])))

                home_city = City.objects.get(
                    name=clean(row["home_city"]),
                    country=home_country,
                )

                Game.objects.update_or_create(
                    id=int(clean(row["id"])),
                    defaults={
                        "country_1": country_1,
                        "country_2": country_2,
                        "goals_country_1": clean(row["goals_country_1"]),
                        "goals_country_2": clean(row["goals_country_2"]),
                        "phase": clean(row["phase"]),
                        "phase_rank": clean(row["phase_rank"]),
                        "date": clean(row["date"]),
                        "home_city": home_city,
                        "home_country": home_country,
                        "world_cup": world_cup,
                        "wikipedia": clean(row["wikipedia"]),
                    },
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} games"))