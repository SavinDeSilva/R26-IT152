import re

from app import db


def _clean_phone(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "nat"):
        return None
    if re.fullmatch(r"\d+\.0+", text):
        return text.split(".", 1)[0]
    try:
        as_float = float(text)
        if as_float == int(as_float) and as_float >= 0:
            return str(int(as_float))
    except ValueError:
        pass
    return text


class Accommodation(db.Model):
    __tablename__ = "accommodation"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.Text, nullable=False)
    category = db.Column("Category", db.Text)
    rooms = db.Column("Rooms", db.Text)
    address = db.Column("Address", db.Text)
    local_authority = db.Column("Local Authority", db.Text)
    normalized_local_authority = db.Column(db.Text)
    web = db.Column("Web", db.Text)
    email = db.Column("Email", db.Text)
    registration_no = db.Column("Registration No:", db.Text)
    tel = db.Column("Tel", db.Text)
    mobile = db.Column("Mobile", db.Text)
    price_range = db.Column("Price Range", db.Text)
    price_min = db.Column(db.Numeric)
    price_max = db.Column(db.Numeric)
    image = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "rooms": self.rooms,
            "address": self.address,
            "local_authority": self.local_authority,
            "normalized_local_authority": self.normalized_local_authority,
            "web": self.web,
            "email": self.email,
            "registration_no": self.registration_no,
            "tel": _clean_phone(self.tel),
            "mobile": _clean_phone(self.mobile),
            "price_range": self.price_range,
            "price_min": float(self.price_min) if self.price_min is not None else None,
            "price_max": float(self.price_max) if self.price_max is not None else None,
            "image": self.image,
        }
