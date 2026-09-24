"""Player profile pictures.

Uploads are re-encoded to two small square sizes and stored in Mongo. They live
in their own ``avatars`` collection keyed by player name, not on the player
document, so the bulk queries behind /players and the leaderboards never drag
image bytes along with them.

Nothing the user uploaded is ever stored or served back: the file is decoded,
cropped, resized and re-encoded, so the bytes leaving here are ones Pillow
wrote.
"""

import hashlib
from datetime import datetime
from io import BytesIO

from bson.binary import Binary
from PIL import Image, ImageOps, UnidentifiedImageError, features

from extensions import mongo

# Largest upload accepted, before resizing. Config.MAX_CONTENT_LENGTH is set a
# little above this so the friendly message below is what people normally see.
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

# Refuse absurd pixel counts before decoding, so a small file that expands into
# gigabytes of bitmap can't take the process down.
MAX_PIXELS = 50_000_000

# Stored sizes, in pixels: "full" for the profile and account headers, "small"
# for the avatars in player lists.
SIZES = {"full": 256, "small": 64}

# WebP is smaller and keeps transparency; JPEG is the fallback if this Pillow
# build has no WebP support.
if features.check("webp"):
    FORMAT, MIMETYPE, EXTENSION = "WEBP", "image/webp", "webp"
else:
    FORMAT, MIMETYPE, EXTENSION = "JPEG", "image/jpeg", "jpg"

QUALITY = 82

# Alpha is flattened onto this when the output format can't keep it. Matches
# --surface-high in main.css, which is what sits behind an avatar.
FLATTEN_BACKGROUND = (26, 30, 38)


def _encode(image, size):
    """Center-cropped square thumbnail of ``image``, as encoded bytes."""
    frame = ImageOps.exif_transpose(image)

    if frame.mode in ("RGBA", "LA", "P"):
        frame = frame.convert("RGBA")
        if FORMAT == "JPEG":
            flat = Image.new("RGB", frame.size, FLATTEN_BACKGROUND)
            flat.paste(frame, mask=frame.getchannel("A"))
            frame = flat
    else:
        frame = frame.convert("RGB")

    square = ImageOps.fit(frame, (size, size), Image.LANCZOS, centering=(0.5, 0.5))

    buf = BytesIO()
    options = {"quality": QUALITY}
    if FORMAT == "WEBP":
        options["method"] = 6
    else:
        options["optimize"] = True
        options["progressive"] = True
    square.save(buf, FORMAT, **options)
    return buf.getvalue()


def store(name, upload):
    """Resize and save ``upload`` as ``name``'s picture.

    Returns an error message, or None when it was stored.
    """
    raw = upload.read(MAX_UPLOAD_BYTES + 1)
    if not raw:
        return "Choose an image to upload."
    if len(raw) > MAX_UPLOAD_BYTES:
        return f"That image is too large (maximum {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)."

    try:
        # verify() checks the file is a real image but leaves it unusable, so
        # the actual decode happens on a second open.
        with Image.open(BytesIO(raw)) as probe:
            probe.verify()
        with Image.open(BytesIO(raw)) as image:
            if image.width * image.height > MAX_PIXELS:
                return "That image has too many pixels."
            image.load()
            variants = {key: _encode(image, px) for key, px in SIZES.items()}
    except (UnidentifiedImageError, OSError, ValueError, MemoryError):
        return "That file isn't an image we can read."

    mongo.db.avatars.replace_one(
        {"name": name},
        {
            "name": name,
            "mimetype": MIMETYPE,
            "etag": hashlib.sha256(variants["full"]).hexdigest()[:32],
            "updated_at": datetime.utcnow(),
            "sizes": {key: Binary(data) for key, data in variants.items()},
        },
        upsert=True,
    )
    return None


def get(name, size="full"):
    """(bytes, mimetype, etag) for a player's picture, or None."""
    doc = mongo.db.avatars.find_one({"name": name})
    if not doc:
        return None
    data = doc["sizes"].get(size) or doc["sizes"].get("full")
    if data is None:
        return None
    return bytes(data), doc.get("mimetype", MIMETYPE), doc.get("etag", "")


def delete(name):
    mongo.db.avatars.delete_one({"name": name})


def etag(name):
    """A player's picture etag, or None when they have no picture.

    Doubles as the cache-buster in page URLs: it only changes when the picture
    does, so a new upload shows up at once without making every other request
    miss the cache.
    """
    doc = mongo.db.avatars.find_one({"name": name}, {"etag": 1})
    return doc.get("etag", "") if doc else None


def etags():
    """{name: etag} for every stored picture, for list pages that would
    otherwise ask once per player."""
    return {d["name"]: d.get("etag", "") for d in mongo.db.avatars.find({}, {"name": 1, "etag": 1})}
