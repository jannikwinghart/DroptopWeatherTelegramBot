from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging
from RoutePlanner import RoutePlanner
from WeatherForecaster import WeatherForecaster
from RouteWeatherEvaluator import RouteWeatherEvaluator
from pprint import pprint

START_LOCATION, TARGET_LOCATION = range(2)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, telegram_token, openrouteservice_apikey, openweathermap_apikey):
        self.routeplanner = RoutePlanner(apikey=openrouteservice_apikey)
        self.weatherforecaster = WeatherForecaster(apikey=openweathermap_apikey)
        self.routeweatherevaluator = RouteWeatherEvaluator()

        self.start_location_coords = None
        self.target_location_coords = None

        # todo: scores = routeweatherevaluator.calculate_route_scores(waypoints, self.weatherforecaster)

        self.updater = Updater(telegram_token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler("start", self.start_handler))
        self.dispatcher.add_handler(CommandHandler("help", self.help_handler))

        # todo: folium map https://github.com/GIScience/openrouteservice-py/blob/master/examples/basic_example.ipynb

        # todo: weather conversation

        routeweather_conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('weather', self.routeweather_conversation_start_handler),
                CommandHandler('wetter', self.routeweather_conversation_start_handler),
            ],
            states={
                START_LOCATION: [
                    MessageHandler(Filters.location, self.routeweather_conversation_startloc_geo_handler),
                    MessageHandler(Filters.text & ~Filters.command, self.routeweather_conversation_startloc_str_handler),
                ],
                TARGET_LOCATION: [
                    MessageHandler(Filters.location, self.routeweather_conversation_targetloc_geo_handler),
                    MessageHandler(Filters.text & ~Filters.command, self.routeweather_conversation_targetloc_str_handler),
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        # todo: weather chat (/weather -> start -> end -> antwort/bild)
        self.dispatcher.add_handler(routeweather_conversation_handler)

        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.message_handler))

    def run_bot(self):
        self.updater.start_polling()
        self.updater.idle()

    def start_handler(self, update: Update, context: CallbackContext):
        """Answer to /start"""
        update.message.reply_text(
            'Hi! My name is DroptopWeather Bot. I will tell you the best time to start your drive. '
            'Send /weather to start my calculations.'
        )

    def help_handler(self, update: Update, context: CallbackContext):
        """Answer to /help"""
        update.message.reply_text(
            "Hi, I'm DroptopWeather Bot. I will tell you the best time to start your drive."
            "Send /weather to start the conversation."
        )

    def routeweather_conversation_start_handler(self, update: Update, context: CallbackContext):
        """Answer to /start"""
        update.message.reply_text(
            "I will tell you the best time to start your drive. "
            "Send /cancel to stop talking to me.\n\n"
            "Where do you want do start your drive?"
        )

        return START_LOCATION

    def routeweather_conversation_startloc_geo_handler(self, update: Update, context: CallbackContext):
        location = update.message.location
        logger.info("User sent the start location %f, %f", location.latitude, location.longitude)
        self.start_location_coords = location.longitude, location.latitude

        update.message.reply_text("Selected this location as starting point.")
        update.message.reply_text("What is the target location of your drive?")
        return TARGET_LOCATION

    def routeweather_conversation_startloc_str_handler(self, update: Update, context: CallbackContext):
        message_text = update.message.text
        logger.info("User sent the start message %s", message_text)

        geocode = self.routeplanner.location_to_coords(message_text)
        geocode_label = geocode["label"]
        self.start_location_coords = geocode["coords"]

        if self.start_location_coords is not None:
            update.message.reply_text(
                "Selected \"{}\" as starting point.".format(geocode_label)
            )

            update.message.reply_text("What is the target location of your drive?")
            return TARGET_LOCATION
        else:
            update.message.reply_text("Could not find a corresponding location. Please try another search term or try to send a geo location.")
            return START_LOCATION

    def routeweather_conversation_targetloc_geo_handler(self, update: Update, context: CallbackContext):
        location = update.message.location
        logger.info("User sent the target location %f, %f", location.latitude, location.longitude)
        self.target_location_coords = location.longitude, location.latitude
        update.message.reply_text("Selected this location as target.")
        self.send_routeweather(update, context)

        return ConversationHandler.END

    def routeweather_conversation_targetloc_str_handler(self, update: Update, context: CallbackContext):
        message_text = update.message.text
        logger.info("User sent the target message %s", message_text)

        geocode = self.routeplanner.location_to_coords(message_text)
        geocode_label = geocode["label"]
        self.target_location_coords = geocode["coords"]

        if self.target_location_coords is not None:
            update.message.reply_text(
                "Selected \"{}\" as target.".format(geocode_label)
            )

            self.send_routeweather(update, context)

            return ConversationHandler.END
        else:
            update.message.reply_text("Could not find a corresponding location. Please try another search term or try to send a geo location.")
            return TARGET_LOCATION

    def send_routeweather(self, update: Update, context: CallbackContext):
        print("Send Routeweather")
        print(self.start_location_coords)
        print(self.target_location_coords)

        distance_between_waypoints_m = 10000
        number_of_waypoints = 5

        route = self.routeplanner.calculate_route(start_coords=self.start_location_coords, end_coords=self.target_location_coords)
        waypoints = self.routeplanner.waypoints = self.routeplanner.calculate_waypoints(route, distance=distance_between_waypoints_m, max_number=number_of_waypoints)
        scores = self.routeweatherevaluator.calculate_route_scores(waypoints, self.weatherforecaster)

        pprint(scores)

        update.message.reply_text("Here are the Results.")

        good_news = []

        for starttime, waypoint_scores in scores.items():
            avg_waypoint_score = sum(waypoint_scores)/len(waypoint_scores)
            if avg_waypoint_score > 0:
                good_news.append(starttime.strftime("%d.%m.%Y %H:%M Uhr") + " " + str(round(avg_waypoint_score, 1)))

        if len(good_news):
            for good_news_msg in good_news:
                update.message.reply_text(good_news_msg)
        else:
            update.message.reply_text("No good timeframe found in the next 48 hours.")

    def cancel(self, update: Update, context: CallbackContext):
        """Cancels the conversation."""
        self.start_location_coords = None
        self.target_location_coords = None

        logger.info("conversation cancelled")
        update.message.reply_text(
            'Goodbye.'
        )

        return ConversationHandler.END

    def message_handler(self, update: Update, context: CallbackContext):
        """Answer to every other message from user"""
        update.message.reply_text("I did not understand. Please try again. \n\nYou can use the commad \"/help\" to learn how to use the bot.")
