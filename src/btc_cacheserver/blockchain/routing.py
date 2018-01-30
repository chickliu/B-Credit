from channels.routing import route
from . import consumers

channel_routing = [
    route("websocket.connect", consumers.ws_connect),
    route("websocket.disconnect", consumers.ws_disconnect),
    route("websocket.account_connect", consumers.ws_account_connect, path=r"^/account/(?P<account_hash>[a-fA-F0-9]{40})/$"),
    route("websocket.account_disconnect", consumers.ws_account_disconnect, path=r"^/account/(?P<account_hash>[a-fA-F0-9]{40})/$"),
]

