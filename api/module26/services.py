"""
Business logic for Module 26 — Emergency Room Patient Alert System
Implements the 5 DFD processes:
  P26.1 — Validate ER Visit Data
  P26.2 — Calculate Triage Score (ESI/CTAS/MTS)
  P26.3 — Generate Time-Sensitive Alerts
  P26.4 — Optimize Resource Allocation
  P26.5 — Generate Throughput Reports
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional
from db import get_collection


def _col(name: str):
    return get_collection(name)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_id(collection_name: str, id_field: str) -> int:
    doc = _col(collection_name).find_one(sort=[(id_field, -1)]) or {}
    return (doc.get(id_field) or 0) + 1


# ── P26.1 — Validate & Register ER Visit ────────────────────────────────────

def create_er_visit(data: dict) -> dict:
    """Validate incoming visit data and persist to er_visits collection."""
    visit_id = _next_id("er_visits", "VisitID")
    log_id   = _next_id("wait_time_logs", "LogID")

    doc = {
        "VisitID":         visit_id,
        "PatientID":       data["patient_id"],
        "chief_complaint": data["chief_complaint"],
        "ArrivalTime":     data.get("arrival_time") or _now(),
        "status":          "waiting",
        "assigned_bed":    data.get("assigned_bed"),
        "TriageID":        None,
        "AlertID":         None,
        "LogID":           log_id,
        "ResourceID":      None,
        "disposition":     None,
        "departure_time":  None,
    }
    _col("er_visits").insert_one(doc)

    # Placeholder wait-time log
    _col("wait_time_logs").insert_one({
        "LogID":    log_id,
        "VisitID":  visit_id,
        "Stage":    "door_to_doctor",
        "Duration": None,
    })

    # If vitals supplied (from M25), store them and run alert check
    vitals_keys = ["bp_systolic", "bp_diastolic", "heart_rate", "spo2", "temperature", "resp_rate"]
    vitals = {k: data[k] for k in vitals_keys if data.get(k) is not None}
    if vitals:
        generate_alerts_from_vitals(visit_id, vitals)

    doc.pop("_id", None)
    return doc


def get_er_visit(visit_id: int) -> Optional[dict]:
    doc = _col("er_visits").find_one({"VisitID": visit_id}, {"_id": 0})
    return doc


def update_er_visit(visit_id: int, updates: dict) -> Optional[dict]:
    result = _col("er_visits").find_one_and_update(
        {"VisitID": visit_id},
        {"$set": updates},
        return_document=True,
    )
    if result:
        result.pop("_id", None)
        # P26.1 side-effect: if visit closed, record wait times
        if updates.get("status") == "complete":
            _record_wait_times_on_close(visit_id)
        # Resource sync: bed assigned / released
        _sync_bed_resource(updates)
    return result


def list_er_visits(status: Optional[str] = None) -> list[dict]:
    query = {"status": status} if status else {}
    return list(_col("er_visits").find(query, {"_id": 0}).sort("ArrivalTime", -1).limit(100))


# ── P26.2 — Calculate Triage Score ──────────────────────────────────────────

def assign_triage(data: dict) -> dict:
    """Persist triage assessment and link to visit; auto-generate alert if urgent."""
    triage_id = _next_id("triages", "TriageID")
    now = _now()

    triage_doc = {
        "TriageID":    triage_id,
        "VisitID":     data["visit_id"],
        "Score":       data["score"],
        "System":      data.get("system", "ESI"),
        "pain_score":  data.get("pain_score"),
        "bp_systolic": data.get("bp_systolic"),
        "bp_diastolic":data.get("bp_diastolic"),
        "heart_rate":  data.get("heart_rate"),
        "spo2":        data.get("spo2"),
        "temperature": data.get("temperature"),
        "resp_rate":   data.get("resp_rate"),
        "notes":       data.get("notes"),
        "assessed_at": now,
    }
    _col("triages").insert_one(triage_doc)

    # Link triage to visit and update status
    _col("er_visits").update_one(
        {"VisitID": data["visit_id"]},
        {"$set": {"TriageID": triage_id, "status": "in_triage"}},
    )

    # P26.3 — auto-alert for Level 1 or 2
    if data["score"] <= 2:
        _create_triage_alert(data["visit_id"], data["score"], data.get("system", "ESI"))

    # Record door-to-triage time
    visit = _col("er_visits").find_one({"VisitID": data["visit_id"]})
    if visit and visit.get("ArrivalTime"):
        door_to_triage = int((now - visit["ArrivalTime"]).total_seconds() / 60)
        _col("wait_time_logs").update_one(
            {"VisitID": data["visit_id"], "Stage": "door_to_triage"},
            {"$set": {"Duration": door_to_triage}},
            upsert=True,
        )

    triage_doc.pop("_id", None)
    return triage_doc


def get_triage_queue() -> list[dict]:
    """P26.2 — Return active visits sorted by triage urgency then arrival time."""
    pipeline = [
        {"$match": {"status": {"$in": ["waiting", "in_triage", "in_treatment"]}}},
        {"$lookup": {
            "from": "triages", "localField": "TriageID",
            "foreignField": "TriageID", "as": "triage",
        }},
        {"$unwind": {"path": "$triage", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "wait_min": {"$dateDiff": {
                "startDate": "$ArrivalTime", "endDate": "$$NOW", "unit": "minute",
            }},
            "triage_score": {"$ifNull": ["$triage.Score", 99]},
        }},
        {"$sort": {"triage_score": 1, "ArrivalTime": 1}},
        {"$project": {
            "_id": 0, "VisitID": 1, "chief_complaint": 1,
            "assigned_bed": 1, "status": 1, "wait_min": 1,
            "triage.Score": 1, "triage.System": 1,
        }},
    ]
    return list(_col("er_visits").aggregate(pipeline))


# ── P26.3 — Generate Time-Sensitive Alerts ───────────────────────────────────

def _create_triage_alert(visit_id: int, score: int, system: str) -> dict:
    alert_id = _next_id("alerts", "AlertID")
    severity = "critical" if score == 1 else "warning"
    doc = {
        "AlertID":      alert_id,
        "VisitID":      visit_id,
        "Type":         f"{system} Level {score} — Immediate attention required",
        "Status":       "active",
        "severity":     severity,
        "triggered_at": _now(),
        "resolved_at":  None,
        "escalated":    False,
    }
    _col("alerts").insert_one(doc)
    _col("er_visits").update_one({"VisitID": visit_id}, {"$set": {"AlertID": alert_id}})
    doc.pop("_id", None)
    return doc


def generate_alerts_from_vitals(visit_id: int, vitals: dict) -> list[dict]:
    """P26.3 — Check vitals against thresholds and create alerts."""
    created = []
    checks = [
        ("spo2",        lambda v: v < 90,  "SpO2 critically low",        "critical"),
        ("heart_rate",  lambda v: v > 140, "Heart rate critically high",  "critical"),
        ("bp_systolic", lambda v: v > 180, "Hypertensive crisis",         "critical"),
        ("resp_rate",   lambda v: v < 10 or v > 30, "Abnormal respiratory rate", "warning"),
        ("temperature", lambda v: v > 39.5, "High fever",                 "warning"),
    ]
    for key, condition, label, severity in checks:
        val = vitals.get(key)
        if val is not None and condition(val):
            alert_id = _next_id("alerts", "AlertID")
            doc = {
                "AlertID":      alert_id,
                "VisitID":      visit_id,
                "Type":         label,
                "Status":       "active",
                "severity":     severity,
                "triggered_at": _now(),
                "resolved_at":  None,
                "escalated":    False,
            }
            _col("alerts").insert_one(doc)
            doc.pop("_id", None)
            created.append(doc)
    return created


def get_active_alerts(severity: Optional[str] = None) -> list[dict]:
    query: dict = {"Status": "active"}
    if severity:
        query["severity"] = severity
    return list(_col("alerts").find(query, {"_id": 0}).sort("triggered_at", 1))


def resolve_alert(alert_id: int, resolved_by: int) -> Optional[dict]:
    doc = _col("alerts").find_one_and_update(
        {"AlertID": alert_id},
        {"$set": {"Status": "resolved", "resolved_at": _now(), "resolved_by": resolved_by}},
        return_document=True,
    )
    if doc:
        doc.pop("_id", None)
    return doc


def escalate_stale_alerts() -> int:
    """Mark critical alerts unresolved for >10 min as escalated. Returns count updated."""
    cutoff = _now() - timedelta(minutes=10)
    result = _col("alerts").update_many(
        {"severity": "critical", "Status": "active",
         "escalated": False, "triggered_at": {"$lte": cutoff}},
        {"$set": {"escalated": True}},
    )
    return result.modified_count


# ── P26.4 — Optimize Resource Allocation ────────────────────────────────────

def get_resources() -> list[dict]:
    """P26.4 — Return all resources with occupancy % and status."""
    pipeline = [
        {"$addFields": {
            "available_units": {"$subtract": ["$total_units", "$occupied_units"]},
            "occupancy_pct": {"$round": [
                {"$multiply": [{"$divide": ["$occupied_units", "$total_units"]}, 100]}, 1,
            ]},
        }},
        {"$addFields": {
            "utilisation_status": {"$switch": {
                "branches": [
                    {"case": {"$gte": ["$occupancy_pct", 90]}, "then": "Critical"},
                    {"case": {"$gte": ["$occupancy_pct", 75]}, "then": "High"},
                ],
                "default": "Normal",
            }},
        }},
        {"$sort": {"occupancy_pct": -1}},
        {"$project": {"_id": 0}},
    ]
    return list(_col("resources").aggregate(pipeline))


def update_resource(resource_id: int, occupied_units: int) -> Optional[dict]:
    doc = _col("resources").find_one_and_update(
        {"ResourceID": resource_id},
        {"$set": {"occupied_units": occupied_units}},
        return_document=True,
    )
    if doc:
        doc.pop("_id", None)
    return doc


def _sync_bed_resource(updates: dict):
    if updates.get("assigned_bed") and "status" not in updates:
        _col("resources").update_one({"Type": "bed"}, {"$inc": {"occupied_units": 1}})
    if updates.get("status") == "complete":
        _col("resources").update_one(
            {"Type": "bed"},
            {"$inc": {"occupied_units": -1}},
        )


def get_crowding_index() -> dict:
    """P26.4 — Compute NEDOCS approximation."""
    total = _col("er_visits").count_documents({"status": {"$ne": "complete"}})
    boarders = _col("er_visits").count_documents({"status": "boarding"})

    pipeline = [
        {"$match": {"status": {"$ne": "complete"}}},
        {"$addFields": {"wait_min": {"$dateDiff": {
            "startDate": "$ArrivalTime", "endDate": "$$NOW", "unit": "minute",
        }}}},
        {"$group": {"_id": None, "max_wait": {"$max": "$wait_min"}}},
    ]
    agg = list(_col("er_visits").aggregate(pipeline))
    longest_wait = agg[0]["max_wait"] if agg else 0

    bed_res = _col("resources").find_one({"Type": "bed"}) or {}
    beds_total    = bed_res.get("total_units", 1)
    beds_occupied = bed_res.get("occupied_units", 0)
    nedocs = round((beds_occupied / beds_total) * 85, 1)

    return {
        "total_er_patients": total,
        "admitted_boarders":  boarders,
        "longest_wait_min":   longest_wait or 0,
        "beds_occupied":      beds_occupied,
        "beds_total":         beds_total,
        "nedocs_approx":      nedocs,
    }


# ── P26.5 — Generate Throughput Reports ─────────────────────────────────────

def get_throughput_report() -> list[dict]:
    """P26.5 — Arrivals, dispositions, and avg LOS grouped by hour (today)."""
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)

    pipeline = [
        {"$match": {"ArrivalTime": {"$gte": today_start}}},
        {"$lookup": {
            "from": "wait_time_logs", "localField": "VisitID",
            "foreignField": "VisitID", "as": "logs",
        }},
        {"$addFields": {
            "hour": {"$hour": "$ArrivalTime"},
            "los_log": {"$first": {"$filter": {
                "input": "$logs",
                "cond": {"$eq": ["$$this.Stage", "los"]},
            }}},
        }},
        {"$group": {
            "_id": "$hour",
            "total_arrivals": {"$sum": 1},
            "discharged": {"$sum": {"$cond": [{"$eq": ["$disposition", "discharged"]}, 1, 0]}},
            "admitted":   {"$sum": {"$cond": [{"$eq": ["$disposition", "admitted"]},   1, 0]}},
            "avg_los_min": {"$avg": "$los_log.Duration"},
        }},
        {"$sort": {"_id": 1}},
        {"$project": {
            "_id": 0, "hour": "$_id",
            "total_arrivals": 1, "discharged": 1, "admitted": 1, "avg_los_min": 1,
        }},
    ]
    return list(_col("er_visits").aggregate(pipeline))


def get_wait_times(visit_id: int) -> list[dict]:
    return list(_col("wait_time_logs").find({"VisitID": visit_id}, {"_id": 0}))


def _record_wait_times_on_close(visit_id: int):
    visit = _col("er_visits").find_one({"VisitID": visit_id})
    if not visit:
        return
    triage = _col("triages").find_one({"VisitID": visit_id})
    arrival = visit.get("ArrivalTime")
    departure = visit.get("departure_time") or _now()

    if arrival and triage:
        door_to_doc = int((triage["assessed_at"] - arrival).total_seconds() / 60)
        _col("wait_time_logs").update_one(
            {"VisitID": visit_id, "Stage": "door_to_doctor"},
            {"$set": {"Duration": door_to_doc}}, upsert=True,
        )

    if arrival:
        los = int((departure - arrival).total_seconds() / 60)
        for stage in ("door_to_disposition", "los"):
            _col("wait_time_logs").update_one(
                {"VisitID": visit_id, "Stage": stage},
                {"$set": {"Duration": los}}, upsert=True,
            )
