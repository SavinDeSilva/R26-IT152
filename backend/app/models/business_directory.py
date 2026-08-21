from app import db


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
            "email": self.email,
            "telephone": self.telephone,
            "fax": self.fax,
        }
