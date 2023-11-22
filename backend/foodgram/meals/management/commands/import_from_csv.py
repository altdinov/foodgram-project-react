import csv

from django.core.management.base import BaseCommand

from meals.models import Product


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_file", nargs="+", type=str)

    def handle(self, *args, **options):
        for csv_file_name in options["csv_file"]:
            reader = csv.DictReader(
                open(csv_file_name, encoding="utf-8"),
                delimiter=",",
                quotechar='"'
            )

            for row in reader:
                if "ingredients.csv" in csv_file_name:
                    Product.objects.create(
                        name=row["name"],
                        measurement_unit=row["measurement_unit"]
                    )
