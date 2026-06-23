from django.db import models


class Continent(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "continent"

    def __str__(self):
        return self.name


class Country(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    continent = models.ForeignKey(
        Continent,
        on_delete=models.PROTECT,
        related_name="countries"
    )

    class Meta:
        db_table = "country"

    def __str__(self):
        return self.name


class City(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="cities"
    )

    class Meta:
        db_table = "city"
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class WorldCup(models.Model):
    year = models.IntegerField(primary_key=True)
    home_country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="world_cups_home_1"
    )
    home_country_second = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="world_cups_home_2",
        null=True,
        blank=True
    )
    home_country_third = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="world_cups_home_3",
        null=True,
        blank=True
    )

    winner = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="won_worldcups",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "world_cup"

    def __str__(self):
        return str(self.year)


class Game(models.Model):
    id = models.IntegerField(primary_key=True)

    country_1 = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="games_as_country_1"
    )
    country_2 = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="games_as_country_2"
    )

    goals_country_1 = models.CharField(max_length=20)
    goals_country_2 = models.CharField(max_length=20)

    phase = models.CharField(max_length=100)
    phase_rank = models.CharField(max_length=100)
    date = models.DateField()

    home_city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="games"
    )
    home_country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="hosted_games"
    )

    world_cup = models.ForeignKey(
        WorldCup,
        on_delete=models.PROTECT,
        related_name="games"
    )

    wikipedia = models.URLField(blank=True)

    class Meta:
        db_table = "game"

    def __str__(self):
        return f"{self.country_1.name} - {self.country_2.name} ({self.date})"