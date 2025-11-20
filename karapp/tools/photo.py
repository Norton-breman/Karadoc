from PIL import Image
import base64
import io
import requests


def make_artwork_base64(path, size=300, quality=60):
    # Charge l’image
    if 'http' in path:
        response = requests.get(path)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
    else:
        img = Image.open(path)

    # Resize pour réduire fortement le poids
    img.thumbnail((size, size))

    # Sauvegarde dans un buffer mémoire
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    artwork_bytes = buffer.getvalue()

    # Encodage Base64 UTF-8
    return base64.b64encode(artwork_bytes).decode('utf-8')