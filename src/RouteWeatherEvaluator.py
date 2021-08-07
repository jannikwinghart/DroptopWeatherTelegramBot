import math
from datetime import datetime, timedelta


class RouteWeatherEvaluator:
    def __init__(self):
        self.weights = {
            "rain": 10,
            "clouds": 5,
            "temp": 5,
            "feels_like": 5,
            "status": 5,
            "daynight": 5
        }

    def map_range(self, value, in_range_min, in_range_max, out_range_min, out_range_max):
        in_range_span = in_range_max - in_range_min
        out_range_span = out_range_max - out_range_min
        value_scaled = float(value - in_range_min) / float(in_range_span)
        return out_range_min + (value_scaled * out_range_span)

    def map_range_capped(self, value, in_range_min, in_range_max, out_range_min, out_range_max):
        if value < in_range_min:
            mapped_value = out_range_min
        elif value > in_range_max:
            mapped_value = out_range_max
        else:
            mapped_value =  self.map_range(value, in_range_min, in_range_max, out_range_min, out_range_max)
        return mapped_value

    def calculate_weather_score(self, current_waypoint_weather):
        """
        calculates a score for the weather [-10, 10]: above 0 is recommended to drive open, below 0 is not recommended
        :param current_waypoint_weather:
        :return:
        """
        attribute_scores = {
            "rain": 0,
            "clouds": 0,
            "temp": 0,
            "feels_like": 0,
            "status": 0,
            "daynight": 0
        }
        # pprint(current_waypoint_weather)

        # rain
        precip_volume_probability = (current_waypoint_weather.get("rain", []).get("1h", 0) + current_waypoint_weather.get("snow", []).get("1h", 0)) * current_waypoint_weather["precipitation_probability"]
        attribute_scores["rain"] = self.map_range_capped(precip_volume_probability, 0, 1, 10, -10)

        # clouds
        attribute_scores["clouds"] = self.map_range_capped(current_waypoint_weather["clouds"], 0, 100, 10, -10)

        # temp
        attribute_scores["temp"] = self.map_range_capped(current_waypoint_weather["temp"]["temp"], 15, 25, -10, 10)

        # feelslike
        attribute_scores["feels_like"] = self.map_range_capped(current_waypoint_weather["temp"]["feels_like"], 15, 25, -10, 10)

        # status
        weather_icon_id = current_waypoint_weather["weather_icon_name"][:2]
        weather_icon_id_scores = {
            "01": 10,       # clear sky
            "02": 8,        # few clouds
            "03": 5,        # scattered clouds
            "04": 3,        # broken clouds
            "09": -10,      # shower rain
            "10": -10,      # rain
            "11": -10,      # thinderstorm
            "13": -10,      # snow
            "50": 0,        # mist
        }
        attribute_scores["status"] = weather_icon_id_scores[weather_icon_id]

        # daynight score
        sunrise_diff_dt = datetime.fromtimestamp(current_waypoint_weather["ref_time"]) - datetime.fromtimestamp(current_waypoint_weather["srise_time"])
        sunrise_diff_minutes = int(sunrise_diff_dt.total_seconds() / 60)
        sunrise_score = self.map_range_capped(sunrise_diff_minutes, 0, 240, -10, 10)
        sunset_diff_dt = datetime.fromtimestamp(current_waypoint_weather["ref_time"]) - datetime.fromtimestamp(current_waypoint_weather["sset_time"])
        sunset_diff_minutes = int(sunset_diff_dt.total_seconds() / 60)
        sunset_score = self.map_range_capped(sunset_diff_minutes, -60, 60, 10, -10)
        attribute_scores["daynight"] = min(sunrise_score, sunset_score)

        # pprint(attribute_scores)

        weighted_sum_attribute_scores = 0
        number_weights = 0
        for attribute in attribute_scores.keys():
            weighted_sum_attribute_scores += self.weights[attribute] * attribute_scores[attribute]
            number_weights += self.weights[attribute]
        score = weighted_sum_attribute_scores / number_weights

        return score

    def calculate_route_scores(self, waypoints, weatherforecaster):
        waypoints_weather = []
        for waypoint_metadata in waypoints:
            waypoints_weather.append({
                "waypoint_metadata": waypoint_metadata,
                "forecast": weatherforecaster.get_forecast(waypoint_metadata["coords"])
            })

        route_duration_max_h = math.ceil(waypoints[-1]["duration"] / 60 / 60)
        start_time = datetime.now().replace(microsecond=0, second=0, minute=0)

        waypoint_weather_scores = dict()

        for timedelta_h in range(48-route_duration_max_h):
            run_start_time = start_time + timedelta(hours=timedelta_h)

            waypoint_weather_scores[run_start_time] = []
            for waypoint_weather in waypoints_weather:
                waypoint_timedelta_rounded_h = round(waypoint_weather["waypoint_metadata"]["duration"] / 60 / 60)
                waypoint_arrival_time = run_start_time + timedelta(hours=waypoint_timedelta_rounded_h)
                current_waypoint_weather = waypoint_weather["forecast"][waypoint_arrival_time]

                weather_score = self.calculate_weather_score(current_waypoint_weather)
                waypoint_weather_scores[run_start_time].append(weather_score)

        return waypoint_weather_scores

