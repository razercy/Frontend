"""
Seed script for Module 26 (Emergency Room Patient Alert System).

Creates/updates default data in the `module26_er` database so frontend and API
have meaningful records even when external modules are not providing input.

Usage (PowerShell):
  1) Activate environment and install requirements.
  2) Ensure MONGO_URI is set, or `.streamlit/secrets.toml` exists.
  3) Run: python seed_module26.py
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from pymongo import MongoClient


def _read_uri_from_secrets() -> str | None:
    secrets_path = Path(".streamlit") / "secrets.toml"
    if not secrets_path.exists():
        return None
    try:
        import tomllib

        data = tomllib.loads(secrets_path.read_text(encoding="utf-8"))
        return data.get("MONGO_URI")
    except Exception:
        return None


def _get_mongo_uri() -> str:
    env_uri = os.getenv("MONGO_URI")
    if env_uri:
        return env_uri
    file_uri = _read_uri_from_secrets()
    if file_uri:
        return file_uri
    raise RuntimeError(
        "MONGO_URI not found. Set environment variable MONGO_URI or add it to .streamlit/secrets.toml"
    )


def _upsert_many(collection, docs: list[dict[str, Any]], key_fields: list[str]) -> None:
    for doc in docs:
        flt = {k: doc[k] for k in key_fields}
        collection.replace_one(flt, doc, upsert=True)


def seed_module26() -> None:
    uri = _get_mongo_uri()
    client = MongoClient(uri)
    db = client["module26_er"]

    now = datetime.now(timezone.utc)

    resources = [
        {"ResourceID": 6001, "Type": "bed", "location": "ER-Wing-A", "total_units": 48, "occupied_units": 43},
        {"ResourceID": 6002, "Type": "doctor", "location": "ER-Wing-A", "total_units": 12, "occupied_units": 10},
        {"ResourceID": 6003, "Type": "nurse", "location": "ER-Wing-A", "total_units": 24, "occupied_units": 19},
        {"ResourceID": 6004, "Type": "ventilator", "location": "ER-Wing-A", "total_units": 8, "occupied_units": 6},
        {"ResourceID": 6005, "Type": "monitor", "location": "ER-Wing-A", "total_units": 20, "occupied_units": 15},
    ]

    triages = [
        {
            "TriageID": 2001,
            "VisitID": 5001,
            "Score": 2,
            "System": "ESI",
            "pain_score": 8,
            "bp_systolic": 158,
            "bp_diastolic": 96,
            "heart_rate": 118,
            "spo2": 91.5,
            "temperature": 37.8,
            "resp_rate": 22,
            "notes": "Default seed data",
            "assessed_at": now - timedelta(minutes=35),
        },
        {
            "TriageID": 2002,
            "VisitID": 5002,
            "Score": 1,
            "System": "ESI",
            "pain_score": 9,
            "bp_systolic": 185,
            "bp_diastolic": 102,
            "heart_rate": 145,
            "spo2": 87.0,
            "temperature": 39.8,
            "resp_rate": 32,
            "notes": "Critical default seed case",
            "assessed_at": now - timedelta(minutes=20),
        },
        {
            "TriageID": 2003,
            "VisitID": 5003,
            "Score": 3,
            "System": "CTAS",
            "pain_score": 5,
            "bp_systolic": 132,
            "bp_diastolic": 84,
            "heart_rate": 102,
            "spo2": 95.0,
            "temperature": 37.2,
            "resp_rate": 20,
            "notes": "Moderate default seed case",
            "assessed_at": now - timedelta(minutes=15),
        },
    ]

    visits = [
        {
            "VisitID": 5001,
            "PatientID": 1001,
            "chief_complaint": "Chest pain with shortness of breath",
            "ArrivalTime": now - timedelta(minutes=40),
            "status": "in_triage",
            "assigned_bed": "ER-03",
            "TriageID": 2001,
            "LogID": 3001,
            "disposition": None,
            "departure_time": None,
        },
        {
            "VisitID": 5002,
            "PatientID": 1002,
            "chief_complaint": "High fever and oxygen desaturation",
            "ArrivalTime": now - timedelta(minutes=26),
            "status": "in_treatment",
            "assigned_bed": "ER-09",
            "TriageID": 2002,
            "LogID": 3002,
            "disposition": None,
            "departure_time": None,
        },
        {
            "VisitID": 5003,
            "PatientID": 1003,
            "chief_complaint": "Road traffic accident",
            "ArrivalTime": now - timedelta(minutes=58),
            "status": "complete",
            "assigned_bed": "ER-05",
            "TriageID": 2003,
            "LogID": 3003,
            "disposition": "admitted",
            "departure_time": now - timedelta(minutes=5),
        },
    ]

    wait_logs = [
        {"LogID": 3001, "VisitID": 5001, "Stage": "door_to_doctor", "Duration": 18},
        {"LogID": 3002, "VisitID": 5002, "Stage": "door_to_doctor", "Duration": 12},
        {"LogID": 3003, "VisitID": 5003, "Stage": "door_to_doctor", "Duration": 9},
        {"LogID": 3004, "VisitID": 5003, "Stage": "door_to_disposition", "Duration": 53},
        {"LogID": 3005, "VisitID": 5003, "Stage": "los", "Duration": 53},
    ]

    alerts = [
        {
            "AlertID": 4001,
            "VisitID": 5001,
            "Type": "ESI Level 2 - Immediate attention required",
            "Status": "active",
            "severity": "warning",
            "triggered_at": now - timedelta(minutes=30),
            "resolved_at": None,
            "escalated": False,
        },
        {
            "AlertID": 4002,
            "VisitID": 5002,
            "Type": "SpO2 critically low",
            "Status": "active",
            "severity": "critical",
            "triggered_at": now - timedelta(minutes=20),
            "resolved_at": None,
            "escalated": True,
        },
    ]

    visit_resources = [
        {"VisitID": 5001, "ResourceID": 6001},
        {"VisitID": 5002, "ResourceID": 6001},
        {"VisitID": 5003, "ResourceID": 6001},
    ]

    _upsert_many(db["resources"], resources, ["ResourceID"])
    _upsert_many(db["triages"], triages, ["TriageID"])
    _upsert_many(db["er_visits"], visits, ["VisitID"])
    _upsert_many(db["wait_time_logs"], wait_logs, ["LogID"])
    _upsert_many(db["alerts"], alerts, ["AlertID"])
    _upsert_many(db["visit_resources"], visit_resources, ["VisitID", "ResourceID"])

    print("Seed completed for database: module26_er")
    for name in ["er_visits", "wait_time_logs", "alerts", "triages", "resources", "visit_resources"]:
        print(f"- {name}: {db[name].count_documents({})}")


if __name__ == "__main__":
    seed_module26()
