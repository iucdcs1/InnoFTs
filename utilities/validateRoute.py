from utilities.models import Route


def validate_route(route: Route, required_places: int) -> bool:
    if route and required_places <= route.available_places:
        return True
    return False
