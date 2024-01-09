from threading import local

localstore = local()


def add_game_id_filter(record):
    record.game_id = getattr(localstore, "game_id", "unknown")
    return True


class AddGameIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        elements = request.path.split("/")
        for i in range(len(elements)):
            if elements[i] == "games" and i + 1 < len(elements):
                localstore.game_id = elements[i + 1]

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        try:
            del localstore.game_id
        except AttributeError:
            pass

        return response
