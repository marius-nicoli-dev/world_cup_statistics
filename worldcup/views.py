from django.shortcuts import render
from django.db.models import Q
from .models import Game, WorldCup, Country, Continent

def games_list(request):
    games = Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup"
    ).order_by("date", "id")

    return render(request, "worldcup/games_list.html", {
        "games": games
    })


def games_filter(request):
    world_cups = WorldCup.objects.all().order_by("year")

    selected_years = request.GET.getlist("world_cup")

    if not selected_years:
        selected_years = [str(wc.year) for wc in world_cups]

    games = Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup"
    ).filter(
        world_cup__year__in=selected_years
    ).order_by("date", "id")

    total_goals = 0

    for game in games:
        if game.goals_country_1.isdigit():
            total_goals += int(game.goals_country_1)

        if game.goals_country_2.isdigit():
            total_goals += int(game.goals_country_2)

    countries = Country.objects.order_by("name")
    continents = Continent.objects.order_by("name")
    world_cups = WorldCup.objects.order_by("year")
    return render(request, "worldcup/games_filter.html", {
        "games": games,
        "world_cups": world_cups,
        "selected_years": selected_years,
        "total_goals": total_goals,
        "countries": countries,
        "continents": continents,
        "world_cups": world_cups,
    })

def country_detail(request, country_id, result_type=None):
    country = Country.objects.get(id=country_id)

    games = Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup"
    ).filter(
        country_1=country
    ) | Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup"
    ).filter(
        country_2=country
    )

    games = games.order_by("date", "id")

    participations = (
        games.values_list("world_cup__year", flat=True)
            .distinct()
            .order_by("world_cup__year")
    )

    participated_world_cups = WorldCup.objects.filter(
        year__in=participations
    ).order_by("year")

    participation_count = participated_world_cups.count()

    stats = {
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
    }

    for game in games:
        if not game.goals_country_1.isdigit() or not game.goals_country_2.isdigit():
            continue

        goals_1 = int(game.goals_country_1)
        goals_2 = int(game.goals_country_2)

        stats["played"] += 1

        if game.country_1_id == country.id:
            goals_for = goals_1
            goals_against = goals_2
        else:
            goals_for = goals_2
            goals_against = goals_1

        stats["goals_for"] += goals_for
        stats["goals_against"] += goals_against

        if goals_for > goals_against:
            stats["wins"] += 1
        elif goals_for == goals_against:
            stats["draws"] += 1
        else:
            stats["losses"] += 1

    filtered_games = []

    for game in games:
        if not game.goals_country_1.isdigit() or not game.goals_country_2.isdigit():
            continue

        goals_1 = int(game.goals_country_1)
        goals_2 = int(game.goals_country_2)

        if game.country_1_id == country.id:
            goals_for = goals_1
            goals_against = goals_2
        else:
            goals_for = goals_2
            goals_against = goals_1

        if result_type == "wins" and goals_for > goals_against:
            filtered_games.append(game)

        elif result_type == "draws" and goals_for == goals_against:
            filtered_games.append(game)

        elif result_type == "losses" and goals_for < goals_against:
            filtered_games.append(game)

    if result_type in ["wins", "draws", "losses"]:
        games = filtered_games

    countries = Country.objects.order_by("name")
    continents = Continent.objects.order_by("name")

    world_cups = WorldCup.objects.order_by("year")

    return render(request, "worldcup/country_detail.html", {
        "country": country,
        "games": games,
        "participation_count": participation_count,
        "participated_world_cups": world_cups,
        "stats": stats,
        "result_type": result_type,
        "countries": countries,
        "continents": continents,
        "participated_world_cups": participated_world_cups,
        "world_cups": world_cups,
    })

def continent_detail(request, continent_id, opponent_continent_id=None, result_type=None):
    continent = Continent.objects.get(id=continent_id)

    opponent_continent = None
    if opponent_continent_id:
        opponent_continent = Continent.objects.get(id=opponent_continent_id)

    all_continent_games = Game.objects.select_related(
        "country_1",
        "country_2",
        "country_1__continent",
        "country_2__continent",
        "home_city",
        "home_country",
        "world_cup",
    ).filter(
        Q(country_1__continent=continent) |
        Q(country_2__continent=continent)
    ).order_by("date", "id")

    games = all_continent_games

    if opponent_continent:
        games = all_continent_games.filter(
            Q(country_1__continent=continent, country_2__continent=opponent_continent) |
            Q(country_1__continent=opponent_continent, country_2__continent=continent)
        )
    if opponent_continent and result_type in ["wins", "draws", "losses"]:
        filtered_games = []

        for game in games:
            if not game.goals_country_1.isdigit() or not game.goals_country_2.isdigit():
                continue

            goals_1 = int(game.goals_country_1)
            goals_2 = int(game.goals_country_2)

            if game.country_1.continent_id == continent.id:
                goals_for = goals_1
                goals_against = goals_2
            else:
                goals_for = goals_2
                goals_against = goals_1

            if result_type == "wins" and goals_for > goals_against:
                filtered_games.append(game)
            elif result_type == "draws" and goals_for == goals_against:
                filtered_games.append(game)
            elif result_type == "losses" and goals_for < goals_against:
                filtered_games.append(game)

        games = filtered_games
    other_continents = Continent.objects.exclude(id=continent.id).order_by("name")

    same_continent_stats = {
        "continent": continent,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
    }

    matches_same_continent = all_continent_games.filter(
        country_1__continent=continent,
        country_2__continent=continent
    )

    for game in matches_same_continent:
        if not game.goals_country_1.isdigit() or not game.goals_country_2.isdigit():
            continue

        goals_1 = int(game.goals_country_1)
        goals_2 = int(game.goals_country_2)

        same_continent_stats["played"] += 1
        same_continent_stats["goals_for"] += goals_1 + goals_2

        if goals_1 == goals_2:
            same_continent_stats["draws"] += 1
        else:
            same_continent_stats["wins"] += 1

    continent_stats = [same_continent_stats]

    for other in other_continents:
        stats = {
            "continent": other,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }

        matches_between = all_continent_games.filter(
            Q(country_1__continent=continent, country_2__continent=other) |
            Q(country_1__continent=other, country_2__continent=continent)
        )

        for game in matches_between:
            if not game.goals_country_1.isdigit() or not game.goals_country_2.isdigit():
                continue

            goals_1 = int(game.goals_country_1)
            goals_2 = int(game.goals_country_2)

            stats["played"] += 1

            if game.country_1.continent_id == continent.id:
                goals_for = goals_1
                goals_against = goals_2
            else:
                goals_for = goals_2
                goals_against = goals_1

            stats["goals_for"] += goals_for
            stats["goals_against"] += goals_against

            if goals_for > goals_against:
                stats["wins"] += 1
            elif goals_for == goals_against:
                stats["draws"] += 1
            else:
                stats["losses"] += 1

        continent_stats.append(stats)
    continents = Continent.objects.order_by("name")
    countries = Country.objects.order_by("name")
    world_cups = WorldCup.objects.order_by("year")
    return render(request, "worldcup/continent_detail.html", {
        "continent": continent,
        "games": games,
        "continent_stats": continent_stats,
        "continents": continents,
        "countries": countries,
        "opponent_continent": opponent_continent,
        "result_type": result_type,
        "world_cups": world_cups,
    })

def world_cup_detail(request, year):
    world_cup = WorldCup.objects.select_related(
        "home_country",
        "home_country_second",
        "home_country_third",
        "winner",
    ).get(year=year)

    games = Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup",
    ).filter(
        world_cup=world_cup
    ).order_by("date", "id")

    total_goals = 0

    for game in games:
        if game.goals_country_1.isdigit():
            total_goals += int(game.goals_country_1)

        if game.goals_country_2.isdigit():
            total_goals += int(game.goals_country_2)

    countries = Country.objects.order_by("name")
    continents = Continent.objects.order_by("name")
    world_cups = WorldCup.objects.order_by("year")

    return render(request, "worldcup/world_cup_detail.html", {
        "world_cup": world_cup,
        "games": games,
        "total_goals": total_goals,
        "countries": countries,
        "continents": continents,
        "world_cups": world_cups,
    })