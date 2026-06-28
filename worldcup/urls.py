from django.urls import path
from . import views

urlpatterns = [
    path("games/", views.games_list, name="games_list"),
    path("games/filter/", views.games_filter, name="games_filter"),

    path(
        "country/<int:country_id>/",
        views.country_detail,
        name="country_detail"
    ),

    path(
        "country/<int:country_id>/<str:result_type>/",
        views.country_detail,
        name="country_detail_filtered"
    ),

    path(
        "continent/<int:continent_id>/vs/<int:opponent_continent_id>/<str:result_type>/",
        views.continent_detail,
        name="continent_detail_vs_result"
    ),

    path(
        "continent/<int:continent_id>/vs/<int:opponent_continent_id>/",
        views.continent_detail,
        name="continent_detail_vs"
    ),

    path("continent/<int:continent_id>/", 
        views.continent_detail, 
        name="continent_detail"
    ),

    path("world-cup/<int:year>/", 
        views.world_cup_detail, 
        name="world_cup_detail"
    ),

    path("city/<int:city_id>/", 
        views.city_detail, 
        name="city_detail"
    ),

    path("team-ranking/", 
        views.team_ranking, 
        name="team_ranking"
    ),

    path("date-filter/",
        views.date_filter,
        name="date_filter"
    ),

    path(
        "world-cup-statistics/",
        views.world_cup_statistics,
        name="world_cup_statistics"
    ),

]