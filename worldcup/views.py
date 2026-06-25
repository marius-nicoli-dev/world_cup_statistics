from django.shortcuts import render
from django.db.models import Q
from .models import Game, WorldCup, Country, Continent, City

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
    cities = City.objects.select_related("country").order_by("name", "country__name")
    
    return render(request, "worldcup/games_filter.html", {
        "games": games,
        "world_cups": world_cups,
        "selected_years": selected_years,
        "total_goals": total_goals,
        "countries": countries,
        "continents": continents,
        "world_cups": world_cups,
        "cities": cities,
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

    edition_stats = []

    all_country_games = Game.objects.filter(
        Q(country_1=country) | Q(country_2=country)
    ).select_related("world_cup").order_by("date", "id")

    for wc in participated_world_cups:
        last_game = (
            all_country_games
            .filter(world_cup=wc)
            .order_by("-date", "-id")
            .first()
        )

        phase = last_game.phase if last_game else ""
        phase_rank = last_game.phase_rank if last_game else ""

        if phase == "final" and phase_rank == "last_2":
            winner = wc.winner

            if winner and winner.id == country.id:
                phase = "winner"
                phase_rank = ""

        edition_stats.append({
            "world_cup": wc,
            "phase": phase,
            "phase_rank": phase_rank,
        })

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
    cities = City.objects.select_related("country").order_by("name", "country__name")

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
        "cities": cities,
        "edition_stats": edition_stats,
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
    cities = City.objects.select_related("country").order_by("name", "country__name")

    return render(request, "worldcup/continent_detail.html", {
        "continent": continent,
        "games": games,
        "continent_stats": continent_stats,
        "continents": continents,
        "countries": countries,
        "opponent_continent": opponent_continent,
        "result_type": result_type,
        "world_cups": world_cups,
        "cities": cities,
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
    cities = City.objects.select_related("country").order_by("name", "country__name")

    return render(request, "worldcup/world_cup_detail.html", {
        "world_cup": world_cup,
        "games": games,
        "total_goals": total_goals,
        "countries": countries,
        "continents": continents,
        "world_cups": world_cups,
        "cities": cities,
    })

def city_detail(request, city_id):
    city = City.objects.select_related("country").get(id=city_id)

    games = Game.objects.select_related(
        "country_1",
        "country_2",
        "home_city",
        "home_country",
        "world_cup",
    ).filter(
        home_city=city
    ).order_by("date", "id")

    cities = City.objects.select_related("country").order_by("name", "country__name")
    countries = Country.objects.order_by("name")
    continents = Continent.objects.order_by("name")
    world_cups = WorldCup.objects.order_by("year")

    return render(request, "worldcup/city_detail.html", {
        "city": city,
        "games": games,
        "cities": cities,
        "countries": countries,
        "continents": continents,
        "world_cups": world_cups,
    })

def get_country_edition_results(country):
    results = []

    participated_years = (
        Game.objects
        .filter(Q(country_1=country) | Q(country_2=country))
        .values_list("world_cup__year", flat=True)
        .distinct()
    )

    world_cups = WorldCup.objects.filter(
        year__in=participated_years
    ).order_by("year")

    for wc in world_cups:
        last_game = (
            Game.objects
            .filter(Q(country_1=country) | Q(country_2=country), world_cup=wc)
            .order_by("-date", "-id")
            .first()
        )

        if not last_game:
            continue

        result = last_game.phase_rank

        if wc.winner and wc.winner_id == country.id:
            result = "winner"

        results.append({
            "world_cup": wc,
            "result": result,
            "phase": last_game.phase,
        })

    return results

def team_ranking(request):
    selected_continent_id = request.GET.get("continent")

    countries = Country.objects.select_related("continent").order_by("name")

    if selected_continent_id:
        countries = countries.filter(continent_id=selected_continent_id)

    result_keys = [
        "winner",
        "last_2",
        "last_3_4",
        "last_4",
        "last_8",
        "last_12",
        "last_13",
        "last_16",
        "last_24",
        "last_32",
        "last_48",
    ]

    ranking = []

    for country in countries:
        counts = {key: 0 for key in result_keys}

        edition_results = get_country_edition_results(country)

        for item in edition_results:
            result = item["result"]

            if result in counts:
                counts[result] += 1

        ranking.append({
            "country": country,
            "counts": counts,
        })

    ranking.sort(
        key=lambda row: (
            -row["counts"]["winner"],
            -row["counts"]["last_2"],
            -row["counts"]["last_3_4"],
            -row["counts"]["last_4"],
            -row["counts"]["last_8"],
            -row["counts"]["last_12"],
            -row["counts"]["last_13"],
            -row["counts"]["last_16"],
            -row["counts"]["last_24"],
            -row["counts"]["last_32"],
            -row["counts"]["last_48"],
            row["country"].name,
        )
    )

    continents = Continent.objects.order_by("name")
    countries = Country.objects.order_by("name")
    cities = City.objects.select_related("country").order_by("name", "country__name")
    world_cups = WorldCup.objects.order_by("year")
    return render(request, "worldcup/team_ranking.html", {
        "ranking": ranking,
        "continents": continents,
        "selected_continent_id": selected_continent_id,
        "result_keys": result_keys,
        "countries": countries,
        "cities": cities,
        "world_cups": world_cups,
    })