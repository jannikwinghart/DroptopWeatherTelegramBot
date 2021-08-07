import logging
import configparser
from Bot import TelegramBot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    config = configparser.ConfigParser()
    try:
        config.read("../config/settings.cfg")
        telegram_token = config["telegram"]["token"]
        openrouteservice_apikey = config["openrouteservice"]["apikey"]
        openweathermap_apikey = config["openweathermap"]["apikey"]
    except:
        config.read("config/settings.cfg")
        telegram_token = config["telegram"]["token"]
        openrouteservice_apikey = config["openrouteservice"]["apikey"]
        openweathermap_apikey = config["openweathermap"]["apikey"]

    telegram_bot = TelegramBot(
        telegram_token=telegram_token,
        openrouteservice_apikey=openrouteservice_apikey,
        openweathermap_apikey=openweathermap_apikey,
    )
    telegram_bot.run_bot()
