from __future__ import annotations

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.crypto import encrypt_text, decrypt_text


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Tourist(db.Model, TimestampMixin):
    __tablename__ = "tourists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, index=True)  # login email
    password_hash = db.Column(db.String(255))  # null if Google-only account
    google_sub = db.Column(db.String(128), unique=True, index=True)  # Google subject id
    auth_provider = db.Column(db.String(32), default="local", nullable=False)  # local | google | both
    phone = db.Column(db.String(512), nullable=False)  # encrypted
    nationality = db.Column(db.String(100), nullable=False)
    passport_or_nic = db.Column(db.String(512), nullable=False)  # encrypted
    photo_path = db.Column(db.String(500))
    document_photo_path = db.Column(db.String(500))
    trip_start = db.Column(db.Date)
    trip_end = db.Column(db.Date)
    hotel_name = db.Column(db.String(255))
    hotel_contact = db.Column(db.String(100))
    last_known_lat = db.Column(db.Float)
    last_known_lng = db.Column(db.Float)

    emergency_contact = db.relationship(
        "EmergencyContact", back_populates="tourist", uselist=False, cascade="all, delete-orphan"
    )
    incidents = db.relationship("Incident", back_populates="tourist", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def set_sensitive(self, phone: str, passport_or_nic: str):
        self.phone = encrypt_text(phone)
        self.passport_or_nic = encrypt_text(passport_or_nic)

    def get_phone(self) -> str | None:
        return decrypt_text(self.phone)

    def get_passport_or_nic(self) -> str | None:
        return decrypt_text(self.passport_or_nic)

    def to_dict(self, reveal_sensitive: bool = False):
        data = {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "auth_provider": self.auth_provider,
            "nationality": self.nationality,
            "trip_start": self.trip_start.isoformat() if self.trip_start else None,
            "trip_end": self.trip_end.isoformat() if self.trip_end else None,
            "hotel_name": self.hotel_name,
            "hotel_contact": self.hotel_contact,
            "photo_path": self.photo_path,
            "document_photo_path": self.document_photo_path,
            "last_known_lat": self.last_known_lat,
            "last_known_lng": self.last_known_lng,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_password": bool(self.password_hash),
        }
        if reveal_sensitive:
            data["phone"] = self.get_phone()
            data["passport_or_nic"] = self.get_passport_or_nic()
        if self.emergency_contact:
            data["emergency_contact"] = self.emergency_contact.to_dict(reveal_sensitive=reveal_sensitive)
        return data


class EmergencyContact(db.Model, TimestampMixin):
    __tablename__ = "emergency_contacts"

    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey("tourists.id"), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(512), nullable=False)  # encrypted
    email = db.Column(db.String(512))  # encrypted
    relationship = db.Column(db.String(100))

    tourist = db.relationship("Tourist", back_populates="emergency_contact")

    def set_sensitive(self, phone: str, email: str | None = None):
        self.phone = encrypt_text(phone)
        self.email = encrypt_text(email) if email else None

    def get_phone(self) -> str | None:
        return decrypt_text(self.phone)

    def get_email(self) -> str | None:
        return decrypt_text(self.email)

    def to_dict(self, reveal_sensitive: bool = False):
        data = {
            "id": self.id,
            "name": self.name,
            "relationship": self.relationship,
        }
        if reveal_sensitive:
            data["phone"] = self.get_phone()
            data["email"] = self.get_email()
        return data


class Hotel(db.Model, TimestampMixin):
    """Optional hotel registry — not seeded from current Excel sources."""

    __tablename__ = "hotels"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact,
            "district": self.district,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }


class Hospital(db.Model, TimestampMixin):
    __tablename__ = "hospitals"

    id = db.Column(db.Integer, primary_key=True)
    district = db.Column(db.String(100))
    name = db.Column(db.String(255), nullable=False)
    local_number = db.Column(db.String(50))
    international_number = db.Column(db.String(50))
    latitude = db.Column(db.Float)  # nullable for hotline-only entries
    longitude = db.Column(db.Float)
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    is_hotline_only = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "district": self.district,
            "name": self.name,
            "local_number": self.local_number,
            "international_number": self.international_number,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_private": self.is_private,
            "is_hotline_only": self.is_hotline_only,
        }


class Station(db.Model, TimestampMixin):
    __tablename__ = "stations"

    id = db.Column(db.Integer, primary_key=True)
    range_name = db.Column(db.String(255), nullable=False)
    division = db.Column(db.String(255))  # often null in source data
    desk = db.Column(db.String(255))
    telephone = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    # True for one representative desk per unique coordinate cluster
    is_dispatchable = db.Column(db.Boolean, default=True, nullable=False)

    officers = db.relationship("Officer", back_populates="station", lazy="dynamic")
    incidents = db.relationship("Incident", back_populates="station", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "range_name": self.range_name,
            "division": self.division,
            "desk": self.desk,
            "telephone": self.telephone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "is_dispatchable": self.is_dispatchable,
            "display_name": self.display_name,
        }

    @property
    def display_name(self) -> str:
        parts = [p for p in [self.range_name, self.division, self.desk] if p]
        return " / ".join(parts) if parts else f"Station {self.id}"


class Officer(db.Model, TimestampMixin):
    __tablename__ = "officers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    badge_number = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    station = db.relationship("Station", back_populates="officers")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "badge_number": self.badge_number,
            "username": self.username,
            "email": self.email,
            "station_id": self.station_id,
            "station": self.station.to_dict() if self.station else None,
            "is_active": self.is_active,
        }


class Incident(db.Model, TimestampMixin):
    __tablename__ = "incidents"

    STATUS_OPEN = "open"
    STATUS_ACKNOWLEDGED = "acknowledged"
    STATUS_DISPATCHED = "dispatched"
    STATUS_CLOSED = "closed"

    TYPE_GENERAL = "general"
    TYPE_MEDICAL = "medical"
    TYPE_RAPE = "rape"
    TYPE_THEFT = "theft"
    TYPE_ACCIDENT = "accident"
    TYPE_HARASSMENT = "harassment"

    VALID_TYPES = {
        TYPE_GENERAL,
        TYPE_MEDICAL,
        TYPE_RAPE,
        TYPE_THEFT,
        TYPE_ACCIDENT,
        TYPE_HARASSMENT,
    }

    TYPE_LABELS = {
        TYPE_GENERAL: "General",
        TYPE_MEDICAL: "Medical",
        TYPE_RAPE: "Rape / Assault",
        TYPE_THEFT: "Theft",
        TYPE_ACCIDENT: "Accident",
        TYPE_HARASSMENT: "Harassment",
    }

    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey("tourists.id"), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey("stations.id"), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.id"))

    incident_type = db.Column(db.String(32), default=TYPE_GENERAL, nullable=False, index=True)
    status = db.Column(db.String(32), default=STATUS_OPEN, nullable=False, index=True)
    initial_lat = db.Column(db.Float, nullable=False)
    initial_lng = db.Column(db.Float, nullable=False)
    distance_to_station_km = db.Column(db.Float)

    triggered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    acknowledged_at = db.Column(db.DateTime)
    dispatched_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)

    hospital_notified_at = db.Column(db.DateTime)
    contact_notified_at = db.Column(db.DateTime)
    hotel_notified_at = db.Column(db.DateTime)

    notes_summary = db.Column(db.Text)
    # One-shot SOS location only — continuous device tracking is disabled
    tracking_active = db.Column(db.Boolean, default=False, nullable=False)
    station_notified_at = db.Column(db.DateTime)

    tourist = db.relationship("Tourist", back_populates="incidents")
    station = db.relationship("Station", back_populates="incidents")
    hospital = db.relationship("Hospital")
    location_pings = db.relationship(
        "LocationPing",
        back_populates="incident",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="LocationPing.recorded_at",
    )
    chat_messages = db.relationship(
        "ChatMessage",
        back_populates="incident",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def to_dict(self, include_pings: bool = False, reveal_tourist: bool = False):
        latest = self.location_pings.order_by(LocationPing.recorded_at.desc()).first()
        data = {
            "id": self.id,
            "tourist_id": self.tourist_id,
            "station_id": self.station_id,
            "hospital_id": self.hospital_id,
            "incident_type": self.incident_type or self.TYPE_GENERAL,
            "incident_type_label": self.TYPE_LABELS.get(
                self.incident_type or self.TYPE_GENERAL, "General"
            ),
            "type": self.incident_type or self.TYPE_GENERAL,
            "status": self.status,
            "initial_lat": self.initial_lat,
            "initial_lng": self.initial_lng,
            "distance_to_station_km": self.distance_to_station_km,
            "triggered_at": self.triggered_at.isoformat() if self.triggered_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "dispatched_at": self.dispatched_at.isoformat() if self.dispatched_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "hospital_notified_at": self.hospital_notified_at.isoformat()
            if self.hospital_notified_at
            else None,
            "contact_notified_at": self.contact_notified_at.isoformat()
            if self.contact_notified_at
            else None,
            "hotel_notified_at": self.hotel_notified_at.isoformat()
            if self.hotel_notified_at
            else None,
            "station_notified_at": self.station_notified_at.isoformat()
            if self.station_notified_at
            else None,
            "notes_summary": self.notes_summary,
            "tracking_active": self.tracking_active,
            "station": self.station.to_dict() if self.station else None,
            "hospital": self.hospital.to_dict() if self.hospital else None,
            "tourist": self.tourist.to_dict(reveal_sensitive=reveal_tourist) if self.tourist else None,
            "latest_ping": latest.to_dict() if latest else None,
        }
        if include_pings:
            data["pings"] = [p.to_dict() for p in self.location_pings.all()]
        return data


class LocationPing(db.Model):
    __tablename__ = "location_pings"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    incident = db.relationship("Incident", back_populates="location_pings")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "accuracy": self.accuracy,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }


class ChatMessage(db.Model):
    """Incident chat between tourist and the assigned (nearest) police station."""

    __tablename__ = "chat_messages"

    ROLE_TOURIST = "tourist"
    ROLE_OFFICER = "officer"
    TYPE_TEXT = "text"
    TYPE_IMAGE = "image"
    TYPE_VOICE = "voice"
    VALID_TYPES = {TYPE_TEXT, TYPE_IMAGE, TYPE_VOICE}

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True)
    sender_role = db.Column(db.String(20), nullable=False)  # tourist | officer
    sender_id = db.Column(db.Integer)  # tourist_id or officer_id
    message_type = db.Column(db.String(20), default=TYPE_TEXT, nullable=False)
    body = db.Column(db.Text)  # text body (optional caption for media)
    media_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    incident = db.relationship("Incident", back_populates="chat_messages")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "sender_role": self.sender_role,
            "sender_id": self.sender_id,
            "message_type": self.message_type,
            "body": self.body,
            "media_path": self.media_path,
            "media_url": f"/uploads/{self.media_path}" if self.media_path else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
