from django.contrib import admin

from .models import Continent, Country, City, WorldCup, Game


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "continent")
    search_fields = ("name", "continent__name")
    list_filter = ("continent",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name", "country__name")
    list_filter = ("country",)


@admin.register(WorldCup)
class WorldCupAdmin(admin.ModelAdmin):
    list_display = (
        "year",
        "home_country",
        "home_country_second",
        "home_country_third",
    )
    search_fields = (
        "year",
        "home_country__name",
        "home_country_second__name",
        "home_country_third__name",
    )


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "country_1",
        "goals_country_1",
        "goals_country_2",
        "country_2",
        "phase",
        "phase_rank",
        "home_city",
        "home_country",
        "world_cup",
    )
    search_fields = (
        "country_1__name",
        "country_2__name",
        "home_city__name",
        "home_country__name",
        "phase",
    )
    list_filter = (
        "world_cup",
        "phase",
        "home_country",
    )