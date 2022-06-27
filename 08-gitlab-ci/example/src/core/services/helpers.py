from crum import get_current_request


def build_absolute_image_uri(image):
    request = get_current_request()
    host = request.get_host()
    abs_url = f"{host}{image.url}"

    if "://" not in host:
        abs_url = f"{request.scheme}://{abs_url}"

    return abs_url
