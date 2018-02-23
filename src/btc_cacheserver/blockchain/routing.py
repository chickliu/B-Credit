from channels.routing import route
from btc_cacheserver.blockchain import consumers, consumers_v2
from django.urls import path

channel_routing = [
    route("check_filter", consumers_v2.CheckFilterConsumer),

    route("websocket.connect", consumers_v2.ws_connect_v2, path=r"^/v2/?$"),
    route("websocket.receive", consumers_v2.ws_receive_v2, path=r"^/v2/?$"),
    route("websocket.disconnect", consumers_v2.ws_disconnect_v2, path=r"^/v2/?$"),
    route("websocket.connect", consumers_v2.ws_connect_v2, path=r"^/v2/account/(?P<account>[a-fA-F0-9]{40})/?$"),
    route("websocket.receive", consumers_v2.ws_receive_v2, path=r"^/v2/account/(?P<account>[a-fA-F0-9]{40})/?$"),
    route("websocket.disconnect", consumers_v2.ws_disconnect_v2, path=r"^/v2/account/(?P<account>[a-fA-F0-9]{40})/?$"),

    route("websocket.connect", consumers.ws_connect, path=r"^/?$"),
    route("websocket.disconnect", consumers.ws_disconnect, path=r"^/?$"),
    route("websocket.connect", consumers.ws_connect, path=r"^/chain/account/(?P<account_hash>[a-fA-F0-9]{40})/?$"),
    route("websocket.disconnect", consumers.ws_disconnect, path=r"^/chain/account/(?P<account_hash>[a-fA-F0-9]{40})/?$"),
]

