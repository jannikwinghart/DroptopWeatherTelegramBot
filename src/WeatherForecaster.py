from pyowm import OWM
from pprint import pprint
from datetime import datetime


class WeatherForecaster:
    def __init__(self, apikey):
        owm = OWM(apikey)
        self.owm_manager = owm.weather_manager()

    def get_forecast(self, coords):
        one_call = self.owm_manager.one_call(lat=coords[0], lon=coords[1], units="metric")

        forecast_elements = {}
        start_day_dt = datetime.fromtimestamp(one_call.forecast_hourly[0].ref_time).replace(microsecond=0, second=0, minute=0, hour=0)

        for forecast_element in one_call.forecast_hourly:
            ref_dt = datetime.fromtimestamp(forecast_element.ref_time)
            forecast_elements[ref_dt] = forecast_element.__dict__

            days_diff = (ref_dt - start_day_dt).days
            forecast_elements[ref_dt]["srise_time"] = one_call.forecast_daily[days_diff].srise_time
            forecast_elements[ref_dt]["sset_time"] = one_call.forecast_daily[days_diff].sset_time

        return forecast_elements

