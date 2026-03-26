"""
Module 26 API Routes — Emergency Room Patient Alert System
REST endpoints mapping to the 5 DFD processes in backend_flow_diagram.dot

  P26.1  POST   /visits              Register ER visit (validate + persist)
         GET    /visits              List visits (optional ?status= filter)
         GET    /visits/{id}         Get single visit
         PUT    /visits/{id}         Update visit status / bed / disposition

  P26.2  POST   /triage              Assign triage score (ESI/CTAS/MTS)
         GET    /triage/queue        Priority-sorted active queue

  P26.3  GET    /alerts              List active alerts (optional ?severity=)
         PUT    /alerts/{id}/resolve Resolve an alert
         POST   /alerts/escalate     Escalate stale critical alerts (cron)
         POST   /intake/vitals       Receive vitals from M25 → auto-alert

  P26.4  GET    /resources           Resource utilisation + status
         PUT    /resources/{id}      Update occupied units
         GET    /resources/crowding  NEDOCS crowding index

  P26.5  GET    /reports/throughput  Hourly throughput report (today)
         GET    /reports/wait-times/{visit_id}  Wait-time stages for a visit

  Inter-module
         POST   /intake/m25-vitals   Receive vital signs from M25
         GET    /export/m27-transfer Active critical alerts for M27
         GET    /export/m29-alerts   Active alerts for M29
"""
import sys
from pathlib import Path

# Allow direct execution (python api/module26/routes.py) by adding project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from api.module26 import services as svc
from api.module26.models import (
    ERVisitIn, ERVisitOut, ERVisitUpdate,
    TriageIn, TriageOut,
    AlertOut, AlertResolve,
    ResourceOut, ResourceUpdate,
    WaitTimeOut, ThroughputRow, CrowdingIndex,
    M25VitalPayload, M27TransferNotification, M29AlertTrigger,
)

router = APIRouter(prefix="/api/module26", tags=["Module 26 — ER Patient Alert"])


# ── P26.1 — ER Visit (Validate & Register) ──────────────────────────────────

@router.post("/visits", response_model=dict, summary="P26.1 Register ER visit")
def register_visit(body: ERVisitIn):
    """Validate and persist a new ER visit. Optionally accepts vitals from M25."""
    doc = svc.create_er_visit(body.model_dump())
    return doc


@router.get("/visits", response_model=list, summary="P26.1 List ER visits")
def list_visits(status: Optional[str] = Query(None, description="Filter by status")):
    return svc.list_er_visits(status)


@router.get("/visits/{visit_id}", response_model=dict, summary="P26.1 Get ER visit")
def get_visit(visit_id: int):
    doc = svc.get_er_visit(visit_id)
    if not doc:
        raise HTTPException(404, f"Visit {visit_id} not found")
    return doc


@router.put("/visits/{visit_id}", response_model=dict, summary="P26.1 Update ER visit")
def update_visit(visit_id: int, body: ERVisitUpdate):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    doc = svc.update_er_visit(visit_id, updates)
    if not doc:
        raise HTTPException(404, f"Visit {visit_id} not found")
    return doc


# ── P26.2 — Triage (Calculate Score) ────────────────────────────────────────

@router.post("/triage", response_model=dict, summary="P26.2 Assign triage score")
def assign_triage(body: TriageIn):
    """Assign ESI/CTAS/MTS triage score. Auto-generates alert for Level 1–2."""
    return svc.assign_triage(body.model_dump())


@router.get("/triage/queue", response_model=list, summary="P26.2 Priority queue")
def triage_queue():
    """Return active ER visits sorted by triage urgency then arrival time."""
    return svc.get_triage_queue()


# ── P26.3 — Alerts (Generate Time-Sensitive Alerts) ─────────────────────────

@router.get("/alerts", response_model=list, summary="P26.3 List active alerts")
def list_alerts(severity: Optional[str] = Query(None, description="critical | warning | info")):
    return svc.get_active_alerts(severity)


@router.put("/alerts/{alert_id}/resolve", response_model=dict, summary="P26.3 Resolve alert")
def resolve_alert(alert_id: int, body: AlertResolve):
    doc = svc.resolve_alert(alert_id, body.resolved_by)
    if not doc:
        raise HTTPException(404, f"Alert {alert_id} not found")
    return doc


@router.post("/alerts/escalate", response_model=dict, summary="P26.3 Escalate stale alerts")
def escalate_alerts():
    """Escalate critical alerts unresolved for >10 min. Call via cron/scheduler."""
    count = svc.escalate_stale_alerts()
    return {"escalated_count": count}


# ── P26.4 — Resources (Optimize Allocation) ─────────────────────────────────

@router.get("/resources", response_model=list, summary="P26.4 Resource utilisation")
def get_resources():
    return svc.get_resources()


@router.put("/resources/{resource_id}", response_model=dict, summary="P26.4 Update resource")
def update_resource(resource_id: int, body: ResourceUpdate):
    doc = svc.update_resource(resource_id, body.occupied_units)
    if not doc:
        raise HTTPException(404, f"Resource {resource_id} not found")
    return doc


@router.get("/resources/crowding", response_model=dict, summary="P26.4 NEDOCS crowding index")
def crowding_index():
    """Return NEDOCS approximation and ER occupancy summary."""
    return svc.get_crowding_index()


# ── P26.5 — Reports (Throughput & Wait Times) ────────────────────────────────

@router.get("/reports/throughput", response_model=list, summary="P26.5 Hourly throughput")
def throughput_report():
    """Arrivals, discharges, admissions, and avg LOS grouped by hour (today)."""
    return svc.get_throughput_report()


@router.get("/reports/wait-times/{visit_id}", response_model=list,
            summary="P26.5 Wait-time stages for a visit")
def wait_times(visit_id: int):
    return svc.get_wait_times(visit_id)


# ── Inter-module endpoints ───────────────────────────────────────────────────

@router.post("/intake/m25-vitals", response_model=dict,
             summary="Receive vital signs from M25 (ICU Vital Signs)")
def intake_m25_vitals(body: M25VitalPayload):
    """
    P26.1 + P26.3 — Accept vital signs forwarded by Module 25.
    Runs threshold checks and auto-generates alerts if values are critical.
    """
    vitals = {k: v for k, v in body.model_dump().items()
              if k not in ("patient_id", "recorded_at") and v is not None}
    # Find the latest active visit for this patient
    visit = _col_visit(body.patient_id)
    if not visit:
        raise HTTPException(404, f"No active ER visit for patient {body.patient_id}")
    alerts = svc.generate_alerts_from_vitals(visit["VisitID"], vitals)
    return {"visit_id": visit["VisitID"], "alerts_generated": len(alerts), "alerts": alerts}


def _col_visit(patient_id: int):
    from db import get_collection
    return get_collection("er_visits").find_one(
        {"PatientID": patient_id, "status": {"$ne": "complete"}},
        {"_id": 0},
        sort=[("ArrivalTime", -1)],
    )


@router.get("/export/m27-transfer", response_model=list,
            summary="Export critical alerts for M27 (Cardiac ICU)")
def export_m27():
    """Return active critical alerts as transfer notifications for Module 27."""
    alerts = svc.get_active_alerts("critical")
    return [
        M27TransferNotification(
            visit_id=a["VisitID"], patient_id=0,
            alert_type=a["Type"], severity=a["severity"],
            triggered_at=a["triggered_at"],
        ).model_dump()
        for a in alerts
    ]


@router.get("/export/m29-alerts", response_model=list,
            summary="Export all active alerts for M29 (Threshold-Based Alerts)")
def export_m29():
    """Return all active alerts as threshold trigger payloads for Module 29."""
    alerts = svc.get_active_alerts()
    return [
        M29AlertTrigger(
            visit_id=a["VisitID"], patient_id=0,
            alert_type=a["Type"], severity=a["severity"],
            triggered_at=a["triggered_at"],
        ).model_dump()
        for a in alerts
    ]