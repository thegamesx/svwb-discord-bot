from urllib.parse import urlparse, urlunparse, quote


# Se encodea la url para transformar carácteres japoneses. Esto asegura que se puedan abrir ciertos links.
def encode_url_path(url):
    # Parsear la URL en partes
    parsed = urlparse(url)

    # Encodear el path (manteniendo los slashes /)
    encoded_path = quote(parsed.path, safe="/")

    # Reconstruir la URL con el path encodeado
    encoded_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    return encoded_url
