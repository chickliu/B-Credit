"""
WSGI config for btc_cacheserver project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import channels.asgi

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc_cacheserver.settings")

channel_layer = channels.asgi.get_channel_layer()
