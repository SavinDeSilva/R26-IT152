from app import db

GUIDE_IMAGE_BASE = "https://www.srilanka.travel/"


def normalize_guide_image_url(raw: str | None) -> str | None:
    """Turn relative/scraped image paths into absolute browser-usable URLs."""
    if not raw:
        return None
    url = str(raw).strip()
    if not url or url.lower() in ("nan", "none"):
        return None

    # Already absolute — collapse accidental double slashes in the path
    if url.startswith("http://") or url.startswith("https://"):
        scheme, rest = url.split("://", 1)
        return f"{scheme}://{rest.replace('//', '/')}"

    # Relative site paths from CSV, e.g. image/tourist_guides/....jpg
    return GUIDE_IMAGE_BASE + url.lstrip("/")


class TouristGuide(db.Model):
    __tablename__ = "tourist_guides"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    guide_type = db.Column(db.Text)
    languages = db.Column(db.Text)
    tel = db.Column(db.Text)
    address = db.Column(db.Text)
    registration_no = db.Column(db.Text)
    email = db.Column(db.Text)
    validity = db.Column(db.Text)
    image_url = db.Column(db.Text)

    def to_dict(self):
        image = normalize_guide_image_url(self.image_url)
        return {
            "id": self.id,
            "name": self.name,
            "guide_type": self.guide_type,
            "category": self.guide_type,
            "languages": self.languages,
            "tel": self.tel,
            "address": self.address,
            "registration_no": self.registration_no,
            "email": self.email,
            "validity": self.validity,
            "image_url": image,
            "image": image,
        }
