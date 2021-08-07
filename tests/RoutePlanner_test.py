import unittest
import configparser
from src.RoutePlanner import RoutePlanner
from pprint import pprint
import os


class RoutePlannerTestCase(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read(os.path.join("..", "config", "settings.cfg"))
        self.openrouteservice_apikey = config["openrouteservice"]["apikey"]

    def test_calculate_route(self):
        pass

    def test_calculate_waypoints_by_distance(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        route = routeplanner.calculate_route(start_coords=(8.34234, 48.23424), end_coords=(8.34423, 48.26424))

        distance_between_waypoints_m = 500
        waypoints = routeplanner.calculate_waypoints_by_distance(route, max_distance=distance_between_waypoints_m)

        last_distance = 0
        for waypoint in waypoints:
            wp_dist = waypoint["distance"] - last_distance
            last_distance = waypoint["distance"]
            if wp_dist > distance_between_waypoints_m:
                self.fail()

    def test_calculate_waypoints_by_number(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        route = routeplanner.calculate_route(start_coords=(8.34234, 48.23424), end_coords=(8.34423, 48.26424))

        number_of_waypoints = 10
        waypoints = routeplanner.calculate_waypoints_by_number(route, number_of_waypoints)

        print(waypoints)

        self.assertEqual(number_of_waypoints, len(waypoints))

    def test_calculate_waypoints(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        route = routeplanner.calculate_route(start_coords=(8.34234, 48.23424), end_coords=(8.34423, 48.26424))

        number_of_waypoints = 10
        distance_between_waypoints_m = 500
        waypoints = routeplanner.calculate_waypoints(route, distance=distance_between_waypoints_m, max_number=number_of_waypoints)
        self.assertTrue(len(waypoints) <= number_of_waypoints)

        number_of_waypoints = 10
        distance_between_waypoints_m = 2000
        waypoints = routeplanner.calculate_waypoints(route, distance=distance_between_waypoints_m, max_number=number_of_waypoints)

        last_distance = 0
        for waypoint in waypoints:
            wp_dist = waypoint["distance"] - last_distance
            last_distance = waypoint["distance"]
            if wp_dist > distance_between_waypoints_m:
                self.fail()

    def test_location_to_coords(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        coords = routeplanner.location_to_coords("Biberach")
        self.assertTrue(9.767544884254292 < coords[0] < 9.820271978120386)
        self.assertTrue(48.08290722648095 < coords[1] < 48.11673326587068)

    def test_locations_to_waypoints(self):
        routeplanner = RoutePlanner(apikey=self.openrouteservice_apikey)
        start_location = "Ingerkingen"
        end_location = "Biberach"
        number_of_waypoints = 10
        distance_between_waypoints_m = 10000

        start_coords = routeplanner.location_to_coords(start_location)
        end_coords = routeplanner.location_to_coords(end_location)

        route = routeplanner.calculate_route(start_coords=start_coords, end_coords=end_coords)

        waypoints = routeplanner.waypoints = routeplanner.calculate_waypoints(route, distance=distance_between_waypoints_m, max_number=number_of_waypoints)
        pprint(waypoints)

        self.assertTrue(len(waypoints) <= number_of_waypoints)


if __name__ == '__main__':
    unittest.main()
