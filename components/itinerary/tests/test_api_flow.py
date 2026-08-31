#!/usr/bin/env python3
"""
End-to-end backend API smoke test.

Usage (backend server must be running on localhost:5002):
    python scripts/test_api_flow.py
    python scripts/test_api_flow.py --token YOUR_JWT
    python scripts/test_api_flow.py --email test@example.com --password secret123
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:5002"


def request(method: str, path: str, token: str | None = None, body: dict | None = None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        payload = e.read().decode()
        try:
            return e.code, json.loads(payload)
        except json.JSONDecodeError:
            return e.code, {"error": payload}


def login_or_register(email: str, password: str) -> str:
    status, data = request("POST", "/api/auth/login", body={"email": email, "password": password})
    if status == 200:
        return data["access_token"]
    status, data = request("POST", "/api/auth/register", body={"email": email, "password": password})
    if status in (200, 201):
        return data["access_token"]
    raise RuntimeError(f"Auth failed ({status}): {data}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token")
    parser.add_argument("--email", default="test@example.com")
    parser.add_argument("--password", default="secret123")
    args = parser.parse_args()

    print("1. Health check...")
    status, data = request("GET", "/api/health")
    assert status == 200 and data.get("status") == "ok", data
    print("   OK")

    token = args.token or login_or_register(args.email, args.password)
    print(f"2. Auth OK (token ...{token[-12:]})")

    print("3. GET /api/attractions?moods=Adventure,Spiritual")
    status, data = request("GET", "/api/attractions?moods=Adventure,Spiritual")
    assert status == 200, data
    attractions = data["attractions"]
    assert len(attractions) > 0, "No attractions returned"
    ids = [a["id"] for a in attractions[:5]]
    print(f"   OK — {len(attractions)} attractions, using IDs: {ids[:3]}...")

    days = 3
    print(f"4. POST /api/trip-input (days={days})")
    status, data = request(
        "POST",
        "/api/trip-input",
        token=token,
        body={
            "days": days,
            "selected_moods": ["Adventure", "Spiritual"],
            "finalized_attractions": ids[:days],
        },
    )
    assert status == 201, data
    trip_id = data["trip"]["trip_id"]
    print(f"   OK — trip_id={trip_id}")

    print("5. POST /api/budget/split")
    status, data = request(
        "POST",
        "/api/budget/split",
        token=token,
        body={"trip_id": trip_id, "budget": 2500, "customize": False},
    )
    assert status == 200, data
    split = data["split"]
    print(f"   OK — accommodation=${split['accommodation']}")

    print("6. GET /api/accommodation")
    status, data = request("GET", f"/api/accommodation?trip_id={trip_id}", token=token)
    assert status == 200, data
    stops = data["stops_by_destination"]
    assert len(stops) > 0, "No destination stops returned"
    picks = {}
    for stop in stops:
        assert stop["hotels"], f"No hotels for {stop['destination']}"
        picks[stop["destination"]] = stop["hotels"][0]["id"]
    print(f"   OK — {len(stops)} destination(s), hotels: {list(picks.values())}")

    print("7. PATCH /api/trip-input (accommodations_by_destination)")
    status, data = request(
        "PATCH",
        f"/api/trip-input/{trip_id}",
        token=token,
        body={"accommodations_by_destination": picks},
    )
    assert status == 200, data
    assert len(data.get("accommodations", [])) == days, data
    print("   OK")

    print("8. POST /api/itinerary/generate")
    status, data = request(
        "POST",
        "/api/itinerary/generate",
        token=token,
        body={"trip_id": trip_id},
    )
    assert status == 201, data
    title = data["itinerary"]["itinerary"].get("title", "Itinerary")
    print(f"   OK — \"{title}\"")

    print("9. GET /api/business-directory")
    status, data = request("GET", f"/api/business-directory?trip_id={trip_id}", token=token)
    assert status == 200, data
    print(f"   OK — {data['count']} businesses")

    print("10. GET /api/travel-agencies")
    status, data = request("GET", f"/api/travel-agencies?trip_id={trip_id}", token=token)
    assert status == 200, data
    print(f"   OK — {data['count']} agencies")

    if data["agencies"]:
        ref_id = data["agencies"][0]["id"]
        print("11. POST /api/saved-references")
        status, data = request(
            "POST",
            "/api/saved-references",
            token=token,
            body={"trip_id": trip_id, "ref_type": "travel_agency", "ref_id": ref_id},
        )
        assert status in (200, 201), data
        print("   OK")

    print("12. GET /api/itinerary/<trip_id>/pdf")
    req = urllib.request.Request(
        f"{BASE}/api/itinerary/{trip_id}/pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            pdf = resp.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        try:
            detail = json.loads(detail)
        except json.JSONDecodeError:
            pass
        raise AssertionError({"status": e.code, "error": detail}) from e
    assert pdf[:4] == b"%PDF", "Response is not a PDF"
    print(f"   OK — PDF size {len(pdf)} bytes")

    print("\nAll backend endpoints passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"\nFAILED: {e}", file=sys.stderr)
        raise SystemExit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
