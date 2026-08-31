from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_

from components.itinerary.backend.models.attraction import Attraction
from components.itinerary.backend.models.business_directory import BusinessDirectory
from components.itinerary.backend.models.tourist_guide import TouristGuide
from components.itinerary.backend.models.travel_agency import TravelAgency
from components.itinerary.backend.utils.trip_helpers import get_user_trip

recommendations_bp = Blueprint("recommendations", __name__)

KNOWN_GUIDE_LANGUAGES = [
    "Arabic",
    "Chinese",
    "Dutch",
    "English",
    "French",
    "German",
    "Greek",
    "Hebrew",
    "Hindi",
    "Hungarian",
    "Italian",
    "Japanese",
    "Korean",
    "Mandarin",
    "Russian",
    "Spanish",
    "Swedish",
    "Tamil",
    "Thai",
    "Urdu",
]


def _trip_destinations(trip):
    attractions = Attraction.query.filter(
        Attraction.id.in_(trip.finalized_attractions or [])
    ).all()
    return list(
        dict.fromkeys(
            a.normalized_destination or a.destination
            for a in attractions
            if (a.normalized_destination or a.destination)
        )
    )


# When a destination has no seeded shops, try nearby areas before global fallback.
NEARBY_DESTINATIONS = {
    "batticaloa": ["Trincomalee", "Ampara", "Pottuvil", "Kalmunai"],
    "trincomalee": ["Batticaloa", "Ampara"],
    "ampara": ["Batticaloa", "Pottuvil", "Trincomalee"],
    "jaffna": ["Trincomalee", "Kilinochchi"],
    "galle": ["Ambalangoda", "Matara", "Hikkaduwa"],
    "matara": ["Galle", "Tangalle"],
    "negombo": ["Colombo", "Gampaha"],
    "colombo": ["Negombo", "Kalutara", "Panadura"],
    "kandy": ["Matale", "Dambulla", "Nuwara Eliya"],
    "nuwara eliya": ["Kandy", "Ella", "Dambulla"],
    "ella": ["Nuwara Eliya", "Badulla", "Wellawaya"],
    "sigiriya": ["Dambulla", "Habarana", "Matale"],
    "dambulla": ["Sigiriya", "Matale", "Kandy"],
}


def _location_filters(model, destinations):
    filters = []
    for dest in destinations:
        if not dest:
            continue
        filters.append(model.normalized_local_authority.ilike(f"%{dest}%"))
        filters.append(model.local_authority.ilike(f"%{dest}%"))
        if hasattr(model, "district"):
            filters.append(model.district.ilike(f"%{dest}%"))
        if hasattr(model, "address"):
            filters.append(model.address.ilike(f"%{dest}%"))
    return filters


def _apply_location_filter(query, model, destinations):
    if not destinations:
        return query
    filters = _location_filters(model, destinations)
    if not filters:
        return query
    return query.filter(or_(*filters))


def _expanded_destinations(destinations):
    expanded = list(destinations or [])
    seen = {d.strip().lower() for d in expanded if d}
    for dest in destinations or []:
        key = (dest or "").strip().lower()
        for nearby in NEARBY_DESTINATIONS.get(key, []):
            if nearby.lower() not in seen:
                expanded.append(nearby)
                seen.add(nearby.lower())
    return expanded


@recommendations_bp.route("/business-directory", methods=["GET"])
@jwt_required()
def list_business_directory():
    trip_id = request.args.get("trip_id")
    destinations = []
    remaining_budget = None
    trip = None
    match_mode = "all"

    if trip_id:
        trip = get_user_trip(trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        destinations = _trip_destinations(trip)
        if trip.budget_split:
            remaining = (
                float(trip.budget_split.food)
                + float(trip.budget_split.shopping)
                + float(trip.budget_split.transport)
            )
            remaining_budget = round(remaining, 2)

    query = BusinessDirectory.query
    results = []
    if destinations:
        results = (
            _apply_location_filter(query, BusinessDirectory, destinations)
            .order_by(BusinessDirectory.business_name)
            .limit(100)
            .all()
        )
        match_mode = "destination"
        if not results:
            nearby = _expanded_destinations(destinations)
            results = (
                _apply_location_filter(BusinessDirectory.query, BusinessDirectory, nearby)
                .order_by(BusinessDirectory.business_name)
                .limit(100)
                .all()
            )
            match_mode = "nearby" if results else "fallback"
        if not results:
            results = (
                BusinessDirectory.query.order_by(BusinessDirectory.business_name)
                .limit(100)
                .all()
            )
            match_mode = "fallback"
    else:
        results = query.order_by(BusinessDirectory.business_name).limit(100).all()

    return jsonify(
        {
            "businesses": [b.to_dict() for b in results],
            "count": len(results),
            "destinations": destinations,
            "remaining_budget": remaining_budget,
            "match_mode": match_mode,
        }
    )


@recommendations_bp.route("/travel-agencies", methods=["GET"])
@jwt_required()
def list_travel_agencies():
    trip_id = request.args.get("trip_id")
    destinations = []

    if trip_id:
        trip = get_user_trip(trip_id)
        if not trip:
            return jsonify({"error": "Trip not found"}), 404
        destinations = _trip_destinations(trip)

    query = TravelAgency.query
    query = _apply_location_filter(query, TravelAgency, destinations)
    results = query.order_by(TravelAgency.name).limit(100).all()

    return jsonify(
        {
            "agencies": [a.to_dict() for a in results],
            "count": len(results),
            "destinations": destinations,
        }
    )


@recommendations_bp.route("/tourist-guides", methods=["GET"])
@jwt_required()
def list_tourist_guides():
    name = (request.args.get("name") or "").strip()
    registration_no = (request.args.get("registration_no") or "").strip()
    guide_type = (request.args.get("guide_type") or request.args.get("category") or "").strip()
    language = (request.args.get("language") or "").strip()

    try:
        limit = min(max(int(request.args.get("limit", 200)), 1), 1000)
    except (TypeError, ValueError):
        limit = 200
    try:
        offset = max(int(request.args.get("offset", 0)), 0)
    except (TypeError, ValueError):
        offset = 0

    query = TouristGuide.query
    if name:
        query = query.filter(TouristGuide.name.ilike(f"%{name}%"))
    if registration_no:
        query = query.filter(TouristGuide.registration_no.ilike(f"%{registration_no}%"))
    if guide_type and guide_type.lower() not in ("all", "all types"):
        query = query.filter(TouristGuide.guide_type.ilike(guide_type))
    if language and language.lower() not in ("all", "all languages"):
        query = query.filter(TouristGuide.languages.ilike(f"%{language}%"))

    total = query.count()
    results = (
        query.order_by(TouristGuide.name)
        .offset(offset)
        .limit(limit)
        .all()
    )

    guide_types = [
        row[0]
        for row in TouristGuide.query.with_entities(TouristGuide.guide_type)
        .distinct()
        .filter(TouristGuide.guide_type.isnot(None))
        .order_by(TouristGuide.guide_type)
        .all()
        if row[0]
    ]

    return jsonify(
        {
            "guides": [g.to_dict() for g in results],
            "count": len(results),
            "total": total,
            "offset": offset,
            "limit": limit,
            "guide_types": guide_types,
            "languages": KNOWN_GUIDE_LANGUAGES,
            "filters": {
                "name": name,
                "registration_no": registration_no,
                "guide_type": guide_type,
                "language": language,
            },
        }
    )
