from flask import Flask

from .admin import admin_cli
from applications.extensions.init_plugins import broadcast_execute


def init_script(app: Flask):
    app.cli.add_command(admin_cli)
    broadcast_execute(app, 'event_finish')
