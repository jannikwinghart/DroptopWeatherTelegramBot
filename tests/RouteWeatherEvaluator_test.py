import unittest
import configparser
from src.RouteWeatherEvaluator import RouteWeatherEvaluator
from src.RoutePlanner import RoutePlanner
from src.WeatherForecaster import WeatherForecaster
from pprint import pprint
import os


class RouteWeatherEvaluatorTestCase(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read(os.path.join("..", "config", "settings.cfg"))
        self.openrouteservice_apikey = config["openrouteservice"]["apikey"]
        self.openweathermap_apikey = config["openweathermap"]["apikey"]
        self.weatherforecaster = WeatherForecaster(apikey=self.openweathermap_apikey)

    def test_calculate_route_scores(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        start_location = "Ingerkingen"
        end_location = "Biberach"
        number_of_waypoints = 10
        distance_between_waypoints_m = 3000

        start_coords = routeplanner.location_to_coords(start_location)
        end_coords = routeplanner.location_to_coords(end_location)

        route = routeplanner.calculate_route(start_coords=start_coords, end_coords=end_coords)

        waypoints = routeplanner.waypoints = routeplanner.calculate_waypoints(route, distance=distance_between_waypoints_m, max_number=number_of_waypoints)

        routeweatherevaluator = RouteWeatherEvaluator()
        scores = routeweatherevaluator.calculate_route_scores(waypoints, self.weatherforecaster)

        pprint(scores)

    def test_calculate_weather_score(self):
        current_waypoint_weather = {
            'clouds': 85,
            'detailed_status': 'overcast clouds',
            'dewpoint': 285.48,
            'heat_index': None,
            'humidex': None,
            'humidity': 66,
            'precipitation_probability': 0,
            'pressure': {
                'press': 1009,
                'sea_level': None
            },
            'rain': {},
            'ref_time': 1628276400,
            'snow': {},
            'srise_time': 1628222586,
            'sset_time': 1628275832,
            'status': 'Clouds',
            'temp': {
                'feels_like': 291.62,
                'temp': 291.96
            },
            'utc_offset': None,
            'uvi': 0,
            'visibility_distance': 10000,
            'weather_code': 804,
            'weather_icon_name': '04n',
            'wnd': {
                'deg': 285,
                'gust': 2.09,
                'speed': 2.04
            }
        }

        current_waypoint_weather = {
            'clouds': 100,
            'detailed_status': 'moderate rain',
            'dewpoint': 13.12,
            'heat_index': None,
            'humidex': None,
            'humidity': 94,
            'precipitation_probability': 1,
            'pressure': {'press': 1009,
                         'sea_level': None},
            'rain': {'1h': 3.79},
            'ref_time': 1628359200,
            'snow': {},
            'srise_time': 1628309067,
            'sset_time': 1628362138,
            'status': 'Rain',
            'temp': {'feels_like': 13.99,
                     'temp': 14.07},
            'utc_offset': None,
            'uvi': 0.03,
            'visibility_distance': 10000,
            'weather_code': 501,
            'weather_icon_name': '10d',
            'wnd': {'deg': 206,
                    'gust': 12.72,
                    'speed': 6.43}
        }

        routeweatherevaluator = RouteWeatherEvaluator()
        score = routeweatherevaluator.calculate_weather_score(current_waypoint_weather)
        print(score)


if __name__ == '__main__':
    unittest.main()
