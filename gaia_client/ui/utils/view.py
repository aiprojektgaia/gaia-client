from gaia_client.ui.utils.router import GaiaRouter


def goto_view(route: str, **kwargs):
    """
    Separating the view logic from the router instance was an attempt to help
    dealing with circular references.

    Any additional arguments passed to this function will also be passed to
    the route callback registered
    """

    router = GaiaRouter.get_instance()
    router.handle_route(route, **kwargs)


def go_home():
    router = GaiaRouter.get_instance()
    router.go_home()
