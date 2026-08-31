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


def _clean_email(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "nat"):
        return None
    return text


class BusinessDirectory(db.Model):
    __tablename__ = "business_directory"

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column("Business Name", db.Text, nullable=False)
    address = db.Column("Address", db.Text)
    local_authority = db.Column("Local Authority", db.Text)
    normalized_local_authority = db.Column(db.Text)
    district = db.Column("District", db.Text)
    website = db.Column("Website", db.Text)
    email = db.Column("Email", db.Text)
    telephone = db.Column("Telephone", db.Text)
    fax = db.Column("Fax", db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "business_name": self.business_name,
            "address": self.address,
            "local_authority": self.local_authority,
            "normalized_local_authority": self.normalized_local_authority,
            "district": self.district,
            "website": self.website,
            "email": _clean_email(self.email),
            "telephone": _clean_phone(self.telephone),
            "fax": _clean_phone(self.fax),
        }
