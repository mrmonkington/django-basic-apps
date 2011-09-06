from PIL import Image
from PIL.ExifTags import TAGS

def show_exif(file):
    """
    Return a dictionary of decoded exif data.

    Thanks to Mike Driscoll: http://is.gd/0EkUar
    """
    exif = {}
    try:
        image = Image.open(file)
        raw = image._getexif()
    except:
        pass
    else:
        for tag, value in raw.items():
            decoded = TAGS.get(tag, tag)
            exif[decoded] = value
    return exif
