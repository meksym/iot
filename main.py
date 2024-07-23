import view
import models
import settings
from aiohttp.web import Application, run_app
from logging.config import dictConfig as logging_config


def get_app():
    app = Application()

    # NOTE: For POST requests to the Device model, send
    # location_id instead of location. The same applies to api_user.

    view.register_model('api', models.Device, app)
    view.register_model('api', models.ApiUser, app)
    view.register_model('api', models.Location, app)

    return app


if __name__ == '__main__':
    logging_config(settings.LOGGING_CONFIG)
    run_app(get_app(), host=settings.HTTP_HOST, port=settings.HTTP_PORT)
