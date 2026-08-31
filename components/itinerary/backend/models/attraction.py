from app import db


class Attraction(db.Model):
    __tablename__ = "attractions"

    id = db.Column(db.Integer, primary_key=True)
    attraction_name = db.Column("Attraction Name", db.Text, nullable=False)
    category = db.Column("Category", db.Text)
    destination = db.Column("Destination", db.Text)
    normalized_destination = db.Column(db.Text)
    details = db.Column("Details", db.Text)
    mood_tag = db.Column(db.Text)
    image = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "attraction_name": self.attraction_name,
            "category": self.category,
            "destination": self.destination,
            "normalized_destination": self.normalized_destination,
            "details": self.details,
            "mood_tag": self.mood_tag,
            "image": self.image,
        }
