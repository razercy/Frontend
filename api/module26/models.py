"""
Pydantic models for Module 26 — Emergency Room Patient Alert System
Entities: ERVisit, Triage, Alert, Resource, WaitTimeLog
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ── Triage ──────────────────────────────────────────────────────────────────

class TriageIn(BaseModel):
    visit_id: int
    system: Literal["ESI", "CTAS", "MTS"] = "ESI"
    score: int = Field(..., ge=1, le=5, description="Priority level 1 (most urgent) – 5")
    pain_score: Optional[int] = Field(None, ge=0, le=10)
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    resp_rate: Optional[int] = None
    notes: Optional[str] = None


class TriageOut(TriageIn):
    triage_id: int
    assessed_at: datetime


# ── ER Visit ─────────────────────────────────────────────────────────────────

class ERVisitIn(BaseModel):
    patient_id: int
    chief_complaint: str
    arrival_time: Optional[datetime] = None   # defaults to now() in service
    assigned_bed: Optional[str] = None
    # Vital signs forwarded from M25 (ICU Vital Signs)
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    resp_rate: Optional[int] = None


class ERVisitOut(BaseModel):
    visit_id: int
    patient_id: int
    chief_complaint: str
    arrival_time: datetime
    status: str
    assigned_bed: Optional[str]
    triage_id: Optional[int]
    alert_id: Optional[int]
    disposition: Optional[str]


class ERVisitUpdate(BaseModel):
    status: Optional[Literal[
        "waiting", "in_triage", "in_treatment", "boarding", "complete"
    ]] = None
    assigned_bed: Optional[str] = None
    disposition: Optional[Literal[
        "discharged", "admitted", "transferred", "left_ama", "expired"
    ]] = None
    departure_time: Optional[datetime] = None


# ── Alert ────────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    alert_id: int
    visit_id: int
    alert_type: str
    severity: Literal["info", "warning", "critical"]
    status: Literal["active", "resolved"]
    triggered_at: datetime
    resolved_at: Optional[datetime]
    escalated: bool


class AlertResolve(BaseModel):
    resolved_by: int   # staff_id


# ── Resource ─────────────────────────────────────────────────────────────────

class ResourceOut(BaseModel):
    resource_id: int
    resource_type: str
    location: Optional[str]
    total_units: int
    occupied_units: int
    occupancy_pct: float
    utilisation_status: Literal["Normal", "High", "Critical"]


class ResourceUpdate(BaseModel):
    occupied_units: int


# ── WaitTime ─────────────────────────────────────────────────────────────────

class WaitTimeOut(BaseModel):
    log_id: int
    visit_id: int
    stage: str
    duration_min: Optional[int]


# ── Reports ──────────────────────────────────────────────────────────────────

class ThroughputRow(BaseModel):
    hour: int
    total_arrivals: int
    discharged: int
    admitted: int
    avg_los_min: Optional[float]


class CrowdingIndex(BaseModel):
    total_er_patients: int
    admitted_boarders: int
    longest_wait_min: int
    beds_occupied: int
    beds_total: int
    nedocs_approx: float


# ── Inter-module payloads ─────────────────────────────────────────────────────

class M25VitalPayload(BaseModel):
    """Incoming vital signs data from Module 25 (ICU Vital Signs)."""
    patient_id: int
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    resp_rate: Optional[int] = None
    recorded_at: Optional[datetime] = None


class M27TransferNotification(BaseModel):
    """Outgoing transfer notification to Module 27 (Cardiac ICU)."""
    visit_id: int
    patient_id: int
    alert_type: str
    severity: str
    triggered_at: datetime


class M29AlertTrigger(BaseModel):
    """Outgoing alert trigger to Module 29 (Threshold-Based Alerts)."""
    visit_id: int
    patient_id: int
    alert_type: str
    severity: str
    triggered_at: datetime
