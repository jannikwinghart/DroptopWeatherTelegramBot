import openrouteservice
from pprint import pprint


class RoutePlanner:
    def __init__(self, apikey):
        self.client = openrouteservice.Client(key=apikey)

    def calculate_route(self, start_coords, end_coords):
        route = self.client.directions((start_coords, end_coords))['routes'][0]
        waypoints_wrong_format = openrouteservice.convert.decode_polyline(route["geometry"])["coordinates"]
        route["waypoint_coords"] = [(waypoint[1], waypoint[0]) for waypoint in waypoints_wrong_format]

        return route

    @staticmethod
    def calculate_waypoints_by_distance(route, max_distance):
        selected_waypoints = []
        wp_distance_range_pct = 1
        distance = max_distance

        while wp_distance_range_pct > 0.2:
            running_duration_s = 0
            running_distance_m = 0
            waypoint_distance_m = 0
            prev_waypoint = {
                "distance": 0,
                "duration": 0,
                "coords": route["waypoint_coords"][0]
            }
            selected_waypoints = [prev_waypoint]

            for segment in route["segments"]:
                for step in segment["steps"]:
                    if step["distance"] > 0:
                        step_waypoint_coords = route["waypoint_coords"][step["way_points"][0]:step["way_points"][1]]
                        step_avg_duration = step["duration"] / len(step_waypoint_coords)
                        step_avg_distance = step["distance"] / len(step_waypoint_coords)

                        for waypoint_coords in step_waypoint_coords:
                            running_duration_s += step_avg_duration
                            running_distance_m += step_avg_distance
                            waypoint_distance_m += step_avg_distance
                            if waypoint_distance_m > distance:
                                selected_waypoints.append(prev_waypoint)
                                waypoint_distance_m = running_distance_m - prev_waypoint["distance"]
                            prev_waypoint = {
                                "distance": running_distance_m,
                                "duration": running_duration_s,
                                "coords": waypoint_coords
                            }

            selected_waypoints.append(prev_waypoint)

            wp_distances = []
            prev_wp = selected_waypoints[0]
            for wp in selected_waypoints[1:]:
                wp_distances.append(wp["distance"] - prev_wp["distance"])
                prev_wp = wp
            wp_distance_range_pct = (max(wp_distances) - min(wp_distances)) / max(wp_distances)
            distance = distance * 0.99

        return selected_waypoints

    def calculate_waypoints_by_number(self, route, number):
        calculated_distance = route["summary"]["distance"] / (number - 2)
        return self.calculate_waypoints_by_distance(route=route, max_distance=calculated_distance)

    def calculate_waypoints(self, route, distance, max_number):
        calculated_number = route["summary"]["distance"] / distance
        if calculated_number > max_number:
            waypoints = self.calculate_waypoints_by_number(route=route, number=max_number)
        else:
            waypoints = self.calculate_waypoints_by_distance(route=route, max_distance=distance)

        return waypoints

    def location_to_coords(self, location_string):
        geocode = self.client.pelias_search(
            text=location_string,
            validate=False,
        )
        coords = geocode['features'][0]["geometry"]["coordinates"]
        return coords
