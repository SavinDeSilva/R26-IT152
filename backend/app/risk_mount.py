"""Mount the Tour Risk Flask app under /api/risk on the unified process."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RISK_ROOT = Path(__file__).resolve().parents[2] / "tour risk manage backend"


def load_risk_flask():
    app_path = RISK_ROOT / "app.py"
    if not app_path.exists():
        raise FileNotFoundError(f"Risk backend missing: {app_path}")

    spec = importlib.util.spec_from_file_location("tour_risk_flask", app_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tour_risk_flask"] = mod

    inserted = str(RISK_ROOT)
    sys.path.insert(0, inserted)
    try:
        spec.loader.exec_module(mod)
    finally:
        if sys.path and sys.path[0] == inserted:
            sys.path.pop(0)
        elif inserted in sys.path:
            sys.path.remove(inserted)
    return mod.app


def mount_risk(flask_app):
    from werkzeug.middleware.dispatcher import DispatcherMiddleware

    try:
        risk_app = load_risk_flask()
    except Exception as exc:
        print(f"WARNING: Tour risk backend not mounted: {exc}")
        return flask_app

    flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {"/api/risk": risk_app})
    print("Tour risk API mounted at /api/risk")
    return flask_app
