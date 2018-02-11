from channels.routing import route
from btc_cacheserver.blockchain import consumers
from django.urls import path

channel_routing = [
    route("websocket.connect", consumers.ws_connect, path=r"^/?$"),
    route("websocket.disconnect", consumers.ws_disconnect, path=r"^/?$"),
    route("websocket.connect", consumers.ws_connect, path=r"^/chain/account/(?P<account_hash>[a-fA-F0-9]{40})/?$"),
    route("websocket.disconnect", consumers.ws_disconnect, path=r"^/chain/account/(?P<account_hash>[a-fA-F0-9]{40})/?$"),
]

