from app import db


class TravelAgency(db.Model):
    __tablename__ = "travel_agencies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("Name", db.Text, nullable=False)
    address = db.Column("Address", db.Text)
    local_authority = db.Column("Local Authority", db.Text)
    normalized_local_authority = db.Column(db.Text)
    website = db.Column("Website", db.Text)
    email = db.Column("Email", db.Text)
    registration_no = db.Column("Registration No.", db.Text)
    licence_no = db.Column("Licence No.", db.Text)
    licence_validity = db.Column("Licence Validity", db.Text)
    telephone = db.Column("Telephone", db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "local_authority": self.local_authority,
            "normalized_local_authority": self.normalized_local_authority,
            "website": self.website,
            "email": self.email,
            "registration_no": self.registration_no,
            "licence_no": self.licence_no,
            "licence_validity": self.licence_validity,
            "telephone": self.telephone,
        }
