import unittest
from src.WeatherForecaster import WeatherForecaster
import datetime
import configparser
import os
from pprint import pprint


class WeatherTestCase(unittest.TestCase):
    def setUp(self):
        config = configparser.ConfigParser()
        config.read(os.path.join("..", "config", "settings.cfg"))
        self.openweathermap_apikey = config["openweathermap"]["apikey"]

    def test_get_weather(self):
        coords = (48.2017, 9.7672)
        datetime_dt = datetime.datetime.now()

        weatherforecaster = WeatherForecaster(apikey=self.openweathermap_apikey)
        forecast_elements = weatherforecaster.get_forecast(coords=coords)

        pprint(forecast_elements)
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
