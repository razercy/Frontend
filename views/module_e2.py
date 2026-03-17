"""
Module 26: Emergency Room Patient Alert System
Category E: ICU & Real-Time Monitoring

Entities    : ERVisit, Triage, Alert, Resource, WaitTime
Triage      : ESI, CTAS, MTS
Time Targets: Door-to-doctor, Door-to-disposition, Length of stay
Features    : Crowding indices, Resource prediction, Flow optimization
SQL         : Queue management algorithms, Time interval calculations
"""
import streamlit as st
from datetime import datetime, timedelta
import random
from db import get_collection

# ─────────────────────────────────────────────
# DB HELPERS
# ─────────────────────────────────────────────

def _col(name: str):
    return get_collection(name, db_name="module26_er")


def _seed_if_empty():
    """Seed MongoDB collections with sample data if they are empty."""
    er_visits = _col("er_visits")
    if er_visits.count_documents({}) > 0:
        return  # already seeded

    now = datetime.utcnow()

    # ── Resources ──────────────────────────────
    resources = _col("resources")
    resources.drop()
    resources.insert_many([
        {"resource_type": "bed",        "location": "ER Main",   "total_units": 48, "occupied_units": 43, "last_updated": now},
        {"resource_type": "doctor",     "location": "ER Main",   "total_units": 12, "occupied_units": 10, "last_updated": now},
        {"resource_type": "nurse",      "location": "ER Main",   "total_units": 24, "occupied_units": 19, "last_updated": now},
        {"resource_type": "ventilator", "location": "ICU Annex", "total_units": 8,  "occupied_units": 6,  "last_updated": now},
        {"resource_type": "monitor",    "location": "ER Main",   "total_units": 20, "occupied_units": 15, "last_updated": now},
    ])

    # ── ER Visits + Triage + Alerts + WaitTimes ─
    complaints = [
        ("Chest pain with shortness of breath", 1, "ESI"),
        ("Altered consciousness",               2, "CTAS"),
        ("Abdominal pain",                      3, "MTS"),
        ("Fever and rash",                      3, "ESI"),
        ("Ankle sprain",                        4, "ESI"),
        ("Laceration on forearm",               4, "ESI"),
        ("Sore throat",                         5, "ESI"),
        ("Headache",                            3, "MTS"),
        ("Difficulty breathing",                2, "ESI"),
        ("Back pain",                           4, "CTAS"),
    ]
    statuses = ["waiting", "in_triage", "in_treatment", "boarding", "complete"]
    dispositions = ["discharged", "admitted", "transferred", "left_ama"]

    visits_col  = _col("er_visits")
    triage_col  = _col("triage")
    alerts_col  = _col("alerts")
    wt_col      = _col("wait_times")

    visits_col.drop(); triage_col.drop(); alerts_col.drop(); wt_col.drop()

    for i, (complaint, priority, system) in enumerate(complaints):
        arrival = now - timedelta(minutes=random.randint(5, 180))
        status  = statuses[i % len(statuses)]
        visit_id = f"ERV-2026-{1800 + i:05d}"

        visits_col.insert_one({
            "visit_id":        visit_id,
            "patient_id":      f"PT-{1000 + i}",
            "arrival_time":    arrival,
            "chief_complaint": complaint,
            "departure_time":  now if status == "complete" else None,
            "disposition":     dispositions[i % len(dispositions)] if status == "complete" else None,
            "status":          status,
            "assigned_bed":    f"ER-{i+1:02d}" if status in ("in_treatment", "boarding") else None,
            "attending_doctor": f"DR-{100 + i}",
        })

        triage_col.insert_one({
            "visit_id":      visit_id,
            "triage_system": system,
            "priority_level": priority,
            "pain_score":    random.randint(3, 10),
            "bp_systolic":   random.randint(110, 170),
            "bp_diastolic":  random.randint(70, 100),
            "heart_rate":    random.randint(65, 130),
            "spo2":          round(random.uniform(92, 99), 1),
            "temperature":   round(random.uniform(36.5, 39.5), 1),
            "resp_rate":     random.randint(14, 28),
            "assessed_by":   f"RN-{200 + i}",
            "assessed_at":   arrival + timedelta(minutes=random.randint(2, 15)),
            "notes":         "",
        })

        if priority <= 2:
            alerts_col.insert_one({
                "visit_id":    visit_id,
                "alert_type":  f"{system} Level {priority} — Immediate attention required",
                "severity":    "critical" if priority == 1 else "warning",
                "triggered_at": arrival + timedelta(minutes=2),
                "resolved_at": None,
                "resolved_by": None,
                "escalated":   False,
            })

        if status == "complete":
            d2d  = random.randint(10, 35)
            los  = random.randint(90, 360)
            wt_col.insert_one({
                "visit_id":                visit_id,
                "door_to_doctor_min":      d2d,
                "door_to_disposition_min": los,
                "length_of_stay_min":      los,
                "recorded_at":             now,
            })

    # ── Throughput (hourly buckets for today) ──
    tp_col = _col("throughput")
    tp_col.drop()
    for h in range(8, 15):
        arrivals   = random.randint(8, 22)
        discharged = int(arrivals * random.uniform(0.6, 0.8))
        admitted   = arrivals - discharged - random.randint(0, 2)
        tp_col.insert_one({
            "hour":       h,
            "arrivals":   arrivals,
            "discharged": discharged,
            "admitted":   max(admitted, 0),
            "avg_los_min": random.randint(180, 210),
        })


# ─────────────────────────────────────────────
# MAIN ENTRY
# ─────────────────────────────────────────────

def module_e2_detail():
    _seed_if_empty()

    st.markdown("Category E > ICU & Real-Time Monitoring > Module 26")
    st.markdown("# Emergency Room Patient Alert System")
    st.markdown(
        "*ER triage priority database, time-sensitive condition alerts, "
        "resource allocation optimization, and wait-time/throughput reporting.*"
    )

    tab = st.radio(
        "",
        ["🏠 Home", "🔗 ER Diagram", "📋 Tables", "🔍 SQL Query", "⚡ Triggers", "📊 Output"],
        horizontal=True,
        key="e2_tabs",
    )
    st.divider()

    if tab == "🏠 Home":
        _home_tab()
    elif tab == "🔗 ER Diagram":
        _er_diagram_tab()
    elif tab == "📋 Tables":
        _tables_tab()
    elif tab == "🔍 SQL Query":
        _sql_tab()
    elif tab == "⚡ Triggers":
        _triggers_tab()
    elif tab == "📊 Output":
        _output_tab()

    st.divider()
    if st.button("⬅ Back to Modules", key="e2_back"):
        st.session_state.view = "category"
        st.rerun()


# ─────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────

def _home_tab():
    st.info(
        "**Emergency Room Patient Alert System** maintains an ER triage priority database, "
        "fires time-sensitive condition alerts, optimises resource allocation, and generates "
        "wait-time and throughput reports using queue-management SQL algorithms."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Input Entities")
        st.success("1️⃣ ERVisit — patient arrival, chief complaint, timestamps")
        st.success("2️⃣ Triage — ESI / CTAS / MTS level, assessed vitals")
        st.success("3️⃣ Alert — condition type, severity, trigger time")
        st.success("4️⃣ Resource — beds, staff, equipment availability")
        st.success("5️⃣ WaitTime — door-to-doctor, door-to-disposition, LOS")

    with col2:
        st.markdown("### Output Entities")
        st.success("1️⃣ Triage Priority Queue (ranked by urgency)")
        st.success("2️⃣ Active Alert Notifications (critical / warning)")
        st.success("3️⃣ Resource Allocation Report (beds used / free)")
        st.success("4️⃣ Wait-Time & Throughput Dashboard")
        st.success("5️⃣ ER Crowding Index (NEDOCS / EDWIN score)")

    st.divider()

    # ── Live metrics from MongoDB ──────────────
    st.markdown("### Live ER Metrics")
    now = datetime.utcnow()

    total_visits  = _col("er_visits").count_documents({"status": {"$ne": "complete"}})
    active_alerts = _col("alerts").count_documents({"resolved_at": None})
    bed_doc       = _col("resources").find_one({"resource_type": "bed"})

    wt_pipeline = [{"$group": {"_id": None, "avg": {"$avg": "$door_to_doctor_min"}}}]
    wt_result   = list(_col("wait_times").aggregate(wt_pipeline))
    avg_d2d      = round(wt_result[0]["avg"], 1) if wt_result else "N/A"

    beds_occ   = bed_doc["occupied_units"] if bed_doc else 0
    beds_total = bed_doc["total_units"]    if bed_doc else 1
    nedocs     = round((beds_occ / beds_total) * 85, 1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ER Visits (Active)", total_visits)
    c2.metric("Active Alerts", active_alerts, delta_color="inverse")
    c3.metric("Avg Door-to-Doctor", f"{avg_d2d} min")
    c4.metric("NEDOCS Score", nedocs, help="60-100 = Overcrowded", delta_color="inverse")

    st.divider()
    st.markdown("### Triage Systems Supported")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("**ESI (Emergency Severity Index)**")
        st.error("Level 1 — Immediate")
        st.warning("Level 2 — Emergent")
        st.info("Level 3 — Urgent")
        st.success("Level 4 — Less Urgent")
        st.success("Level 5 — Non-Urgent")
    with t2:
        st.markdown("**CTAS (Canadian Triage & Acuity Scale)**")
        st.error("Level 1 — Resuscitation")
        st.warning("Level 2 — Emergent")
        st.info("Level 3 — Urgent")
        st.success("Level 4 — Less Urgent")
        st.success("Level 5 — Non-Urgent")
    with t3:
        st.markdown("**MTS (Manchester Triage System)**")
        st.error("🔴 Immediate (0 min)")
        st.warning("🟠 Very Urgent (10 min)")
        st.info("🟡 Urgent (60 min)")
        st.success("🟢 Standard (120 min)")
        st.success("⚪ Non-Urgent (240 min)")

    st.divider()
    st.markdown("### Key Time Targets")
    st.table({
        "Metric": ["Door-to-Doctor", "Door-to-Disposition", "Length of Stay (Admitted)", "Length of Stay (Discharged)"],
        "Target": ["≤ 30 min", "≤ 4 hours", "≤ 6 hours", "≤ 4 hours"],
    })


# ─────────────────────────────────────────────
# ER DIAGRAM
# ─────────────────────────────────────────────

def _er_diagram_tab():
    st.markdown("### Entity Relationship Diagram")
    st.code("""
┌──────────────────────┐        ┌─────────────────────────┐
│       ERVisit        │        │         Triage           │
├──────────────────────┤        ├─────────────────────────┤
│ PK visit_id          │──1──┐  │ PK triage_id             │
│    patient_id (FK)   │     └─►│ FK visit_id              │
│    arrival_time      │        │    triage_system         │
│    chief_complaint   │        │    priority_level (1-5)  │
│    departure_time    │        │    assessed_at           │
│    assigned_bed      │        │    assessed_by (FK)      │
│    status            │        │    pain_score            │
└──────────────────────┘        └─────────────────────────┘
          │ 1
          ▼ N
┌──────────────────────┐        ┌─────────────────────────┐
│        Alert         │        │        WaitTime          │
├──────────────────────┤        ├─────────────────────────┤
│ PK alert_id          │        │ PK waittime_id           │
│ FK visit_id          │        │ FK visit_id              │
│    alert_type        │        │    door_to_doctor_min    │
│    severity          │        │    door_to_disposition_m │
│    triggered_at      │        │    length_of_stay_min    │
│    resolved_at       │        │    recorded_at           │
└──────────────────────┘        └─────────────────────────┘
          │ N
          ▼ 1
┌──────────────────────┐
│       Resource       │
├──────────────────────┤
│ PK resource_id       │
│    resource_type     │
│    total_units       │
│    occupied_units    │
│    last_updated      │
└──────────────────────┘
""", language="text")


# ─────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────

def _tables_tab():
    st.markdown("### Database Tables (MongoDB Collections)")

    collections = {
        "er_visits":  "ERVisit",
        "triage":     "Triage",
        "alerts":     "Alert",
        "resources":  "Resource",
        "wait_times": "WaitTime",
        "throughput": "Throughput",
    }

    rows = {"Collection": [], "Entity": [], "Documents": [], "Status": []}
    for col_name, entity in collections.items():
        count = _col(col_name).count_documents({})
        rows["Collection"].append(col_name)
        rows["Entity"].append(entity)
        rows["Documents"].append(count)
        rows["Status"].append("✅ Active" if count > 0 else "⚠️ Empty")

    st.table(rows)

    st.divider()
    st.markdown("#### DDL Schemas (equivalent SQL for reference)")

    with st.expander("er_visits"):
        st.code("""
CREATE TABLE er_visits (
    visit_id          VARCHAR(20) PRIMARY KEY,
    patient_id        VARCHAR(20) NOT NULL,
    arrival_time      DATETIME NOT NULL DEFAULT NOW(),
    chief_complaint   TEXT NOT NULL,
    departure_time    DATETIME,
    disposition       ENUM('discharged','admitted','transferred','left_ama','expired'),
    status            ENUM('waiting','in_triage','in_treatment','boarding','complete')
                      NOT NULL DEFAULT 'waiting',
    assigned_bed      VARCHAR(10),
    attending_doctor  VARCHAR(20),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);
""", language="sql")

    with st.expander("triage"):
        st.code("""
CREATE TABLE triage (
    visit_id          VARCHAR(20) NOT NULL UNIQUE,
    triage_system     ENUM('ESI','CTAS','MTS') NOT NULL DEFAULT 'ESI',
    priority_level    TINYINT NOT NULL CHECK (priority_level BETWEEN 1 AND 5),
    pain_score        TINYINT CHECK (pain_score BETWEEN 0 AND 10),
    bp_systolic       SMALLINT,
    bp_diastolic      SMALLINT,
    heart_rate        SMALLINT,
    spo2              DECIMAL(5,2),
    temperature       DECIMAL(4,1),
    resp_rate         TINYINT,
    assessed_by       VARCHAR(20) NOT NULL,
    assessed_at       DATETIME NOT NULL DEFAULT NOW(),
    notes             TEXT,
    FOREIGN KEY (visit_id) REFERENCES er_visits(visit_id)
);
""", language="sql")

    with st.expander("alerts"):
        st.code("""
CREATE TABLE alerts (
    visit_id          VARCHAR(20) NOT NULL,
    alert_type        VARCHAR(100) NOT NULL,
    severity          ENUM('info','warning','critical') NOT NULL,
    triggered_at      DATETIME NOT NULL DEFAULT NOW(),
    resolved_at       DATETIME,
    resolved_by       VARCHAR(20),
    escalated         BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (visit_id) REFERENCES er_visits(visit_id)
);
""", language="sql")

    with st.expander("resources"):
        st.code("""
CREATE TABLE resources (
    resource_type     ENUM('bed','doctor','nurse','ventilator','monitor') NOT NULL,
    location          VARCHAR(50),
    total_units       SMALLINT NOT NULL,
    occupied_units    SMALLINT NOT NULL DEFAULT 0,
    last_updated      DATETIME NOT NULL DEFAULT NOW(),
    CHECK (occupied_units <= total_units)
);
""", language="sql")

    with st.expander("wait_times"):
        st.code("""
CREATE TABLE wait_times (
    visit_id                VARCHAR(20) NOT NULL UNIQUE,
    door_to_doctor_min      SMALLINT,
    door_to_disposition_min SMALLINT,
    length_of_stay_min      SMALLINT,
    recorded_at             DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (visit_id) REFERENCES er_visits(visit_id)
);
""", language="sql")


# ─────────────────────────────────────────────
# SQL QUERIES
# ─────────────────────────────────────────────

def _sql_tab():
    st.markdown("### Sample SQL Queries")

    query_options = [
        "Triage Priority Queue (Queue Management)",
        "Time Interval Calculations (Door-to-Doctor, LOS)",
        "ER Crowding Index (NEDOCS Approximation)",
        "Resource Utilisation & Prediction",
        "Throughput Report by Hour",
        "Unresolved Critical Alerts",
    ]
    sel = st.selectbox("Select a query", query_options, key="e2_query_sel")

    queries = {
        "Triage Priority Queue (Queue Management)": """
-- Real-time triage priority queue ordered by urgency and wait time
SELECT
    ev.visit_id,
    ev.chief_complaint,
    t.triage_system,
    t.priority_level,
    TIMESTAMPDIFF(MINUTE, ev.arrival_time, NOW())  AS wait_min,
    ev.assigned_bed,
    ev.status
FROM er_visits ev
JOIN triage t ON ev.visit_id = t.visit_id
WHERE ev.status IN ('waiting', 'in_triage', 'in_treatment')
ORDER BY
    t.priority_level ASC,
    ev.arrival_time  ASC;
""",
        "Time Interval Calculations (Door-to-Doctor, LOS)": """
SELECT
    ev.visit_id,
    ev.arrival_time,
    ev.departure_time,
    TIMESTAMPDIFF(MINUTE, ev.arrival_time, t.assessed_at)   AS door_to_triage_min,
    wt.door_to_doctor_min,
    wt.door_to_disposition_min,
    wt.length_of_stay_min,
    CASE WHEN wt.door_to_doctor_min <= 30  THEN 'On Target' ELSE 'Breached' END AS d2d_status,
    CASE WHEN wt.length_of_stay_min <= 240 THEN 'On Target' ELSE 'Breached' END AS los_status
FROM er_visits ev
JOIN triage    t  ON ev.visit_id = t.visit_id
JOIN wait_times wt ON ev.visit_id = wt.visit_id
ORDER BY ev.arrival_time DESC LIMIT 50;
""",
        "ER Crowding Index (NEDOCS Approximation)": """
SELECT
    COUNT(*)                                                AS total_er_patients,
    SUM(CASE WHEN ev.status = 'boarding' THEN 1 ELSE 0 END) AS admitted_boarders,
    MAX(TIMESTAMPDIFF(MINUTE, ev.arrival_time, NOW()))      AS longest_wait_min,
    (SELECT occupied_units FROM resources WHERE resource_type='bed' LIMIT 1) AS beds_occupied,
    (SELECT total_units    FROM resources WHERE resource_type='bed' LIMIT 1) AS beds_total,
    ROUND(
        (COUNT(*) / NULLIF(
            (SELECT total_units FROM resources WHERE resource_type='bed' LIMIT 1), 0)
        ) * 85, 1
    ) AS nedocs_approx
FROM er_visits ev WHERE ev.status NOT IN ('complete');
""",
        "Resource Utilisation & Prediction": """
SELECT
    resource_type,
    location,
    total_units,
    occupied_units,
    (total_units - occupied_units)               AS available_units,
    ROUND(occupied_units / total_units * 100, 1) AS occupancy_pct,
    CASE
        WHEN occupied_units / total_units >= 0.90 THEN '🔴 Critical'
        WHEN occupied_units / total_units >= 0.75 THEN '🟠 High'
        ELSE '🟢 Normal'
    END AS utilisation_status
FROM resources ORDER BY occupancy_pct DESC;
""",
        "Throughput Report by Hour": """
SELECT
    HOUR(ev.arrival_time)                                   AS hour_of_day,
    COUNT(*)                                                AS total_arrivals,
    SUM(CASE WHEN ev.disposition='discharged' THEN 1 ELSE 0 END) AS discharged,
    SUM(CASE WHEN ev.disposition='admitted'   THEN 1 ELSE 0 END) AS admitted,
    ROUND(AVG(wt.length_of_stay_min), 1)                    AS avg_los_min
FROM er_visits ev
LEFT JOIN wait_times wt ON ev.visit_id = wt.visit_id
WHERE DATE(ev.arrival_time) = CURDATE()
GROUP BY HOUR(ev.arrival_time)
ORDER BY hour_of_day;
""",
        "Unresolved Critical Alerts": """
SELECT
    a.visit_id,
    ev.assigned_bed,
    a.alert_type,
    a.severity,
    a.triggered_at,
    TIMESTAMPDIFF(MINUTE, a.triggered_at, NOW()) AS minutes_open,
    a.escalated
FROM alerts a
JOIN er_visits ev ON a.visit_id = ev.visit_id
WHERE a.severity = 'critical' AND a.resolved_at IS NULL
ORDER BY a.triggered_at ASC;
""",
    }

    st.code(queries[sel], language="sql")

    if st.button("▶️ Execute Query", key="e2_exec"):
        st.success("Query executed — results from MongoDB:")
        now = datetime.utcnow()

        if sel == "Triage Priority Queue (Queue Management)":
            pipeline = [
                {"$match": {"status": {"$in": ["waiting", "in_triage", "in_treatment"]}}},
                {"$lookup": {
                    "from": "triage",
                    "localField": "visit_id",
                    "foreignField": "visit_id",
                    "as": "triage_info"
                }},
                {"$unwind": "$triage_info"},
                {"$sort": {"triage_info.priority_level": 1, "arrival_time": 1}},
                {"$limit": 10},
            ]
            rows = list(_col("er_visits").aggregate(pipeline))
            if rows:
                st.table({
                    "Visit ID":       [r["visit_id"] for r in rows],
                    "Chief Complaint": [r["chief_complaint"] for r in rows],
                    "System":         [r["triage_info"]["triage_system"] for r in rows],
                    "Priority":       [r["triage_info"]["priority_level"] for r in rows],
                    "Wait (min)":     [int((now - r["arrival_time"]).total_seconds() / 60) for r in rows],
                    "Status":         [r["status"] for r in rows],
                })

        elif sel == "Resource Utilisation & Prediction":
            rows = list(_col("resources").find({}, {"_id": 0}))
            if rows:
                def status(r):
                    pct = r["occupied_units"] / r["total_units"]
                    return "🔴 Critical" if pct >= 0.90 else ("🟠 High" if pct >= 0.75 else "🟢 Normal")
                st.table({
                    "Resource":    [r["resource_type"] for r in rows],
                    "Total":       [r["total_units"] for r in rows],
                    "Occupied":    [r["occupied_units"] for r in rows],
                    "Available":   [r["total_units"] - r["occupied_units"] for r in rows],
                    "Occupancy %": [f"{r['occupied_units']/r['total_units']*100:.1f}%" for r in rows],
                    "Status":      [status(r) for r in rows],
                })

        elif sel == "ER Crowding Index (NEDOCS Approximation)":
            active = list(_col("er_visits").find({"status": {"$ne": "complete"}}))
            boarders = sum(1 for v in active if v["status"] == "boarding")
            bed_doc  = _col("resources").find_one({"resource_type": "bed"})
            beds_occ   = bed_doc["occupied_units"] if bed_doc else 0
            beds_total = bed_doc["total_units"]    if bed_doc else 1
            longest    = max((int((now - v["arrival_time"]).total_seconds() / 60) for v in active), default=0)
            nedocs     = round((len(active) / beds_total) * 85, 1)
            st.table({
                "Total ER Patients": [len(active)],
                "Admitted Boarders": [boarders],
                "Longest Wait (min)": [longest],
                "Beds Occupied":     [beds_occ],
                "Beds Total":        [beds_total],
                "NEDOCS Approx":     [nedocs],
            })

        elif sel == "Unresolved Critical Alerts":
            rows = list(_col("alerts").find({"severity": "critical", "resolved_at": None}))
            if rows:
                st.table({
                    "Visit ID":    [r["visit_id"] for r in rows],
                    "Alert Type":  [r["alert_type"] for r in rows],
                    "Severity":    [r["severity"] for r in rows],
                    "Triggered At": [r["triggered_at"].strftime("%H:%M") for r in rows],
                    "Minutes Open": [int((now - r["triggered_at"]).total_seconds() / 60) for r in rows],
                    "Escalated":   [r["escalated"] for r in rows],
                })
            else:
                st.info("No unresolved critical alerts.")

        elif sel == "Throughput Report by Hour":
            rows = list(_col("throughput").find({}, {"_id": 0}).sort("hour", 1))
            if rows:
                st.table({
                    "Hour":         [f"{r['hour']:02d}:00" for r in rows],
                    "Arrivals":     [r["arrivals"] for r in rows],
                    "Discharged":   [r["discharged"] for r in rows],
                    "Admitted":     [r["admitted"] for r in rows],
                    "Avg LOS (min)":[r["avg_los_min"] for r in rows],
                })

        else:
            rows = list(_col("wait_times").find({}, {"_id": 0}).limit(10))
            if rows:
                st.table({
                    "Visit ID":    [r["visit_id"] for r in rows],
                    "D2D (min)":   [r.get("door_to_doctor_min") for r in rows],
                    "D2Disp (min)":[r.get("door_to_disposition_min") for r in rows],
                    "LOS (min)":   [r.get("length_of_stay_min") for r in rows],
                })


# ─────────────────────────────────────────────
# TRIGGERS
# ─────────────────────────────────────────────

def _triggers_tab():
    st.markdown("### Database Triggers")

    with st.expander("🔔 trg_triage_alert — Fire alert on high-priority triage", expanded=True):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_triage_alert
AFTER INSERT ON triage
FOR EACH ROW
BEGIN
    IF NEW.priority_level <= 2 THEN
        INSERT INTO alerts (visit_id, alert_type, severity)
        VALUES (
            NEW.visit_id,
            CONCAT(NEW.triage_system, ' Level ', NEW.priority_level, ' — Immediate attention required'),
            CASE WHEN NEW.priority_level = 1 THEN 'critical' ELSE 'warning' END
        );
    END IF;
END$

DELIMITER ;
""", language="sql")

    with st.expander("⏱️ trg_wait_time_log — Record time intervals on departure"):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_wait_time_log
AFTER UPDATE ON er_visits
FOR EACH ROW
BEGIN
    DECLARE v_door_to_doc   SMALLINT;
    DECLARE v_door_to_disp  SMALLINT;
    DECLARE v_los           SMALLINT;

    IF NEW.status = 'complete' AND OLD.status <> 'complete' THEN
        SELECT TIMESTAMPDIFF(MINUTE, NEW.arrival_time, MIN(assessed_at))
        INTO v_door_to_doc FROM triage WHERE visit_id = NEW.visit_id;

        SET v_door_to_disp = TIMESTAMPDIFF(MINUTE, NEW.arrival_time, NEW.departure_time);
        SET v_los          = v_door_to_disp;

        INSERT INTO wait_times
            (visit_id, door_to_doctor_min, door_to_disposition_min, length_of_stay_min)
        VALUES (NEW.visit_id, v_door_to_doc, v_door_to_disp, v_los)
        ON DUPLICATE KEY UPDATE
            door_to_doctor_min      = v_door_to_doc,
            door_to_disposition_min = v_door_to_disp,
            length_of_stay_min      = v_los,
            recorded_at             = NOW();
    END IF;
END$

DELIMITER ;
""", language="sql")

    with st.expander("🛏️ trg_resource_update — Adjust bed count on admission/discharge"):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_resource_update
AFTER UPDATE ON er_visits
FOR EACH ROW
BEGIN
    IF NEW.assigned_bed IS NOT NULL AND OLD.assigned_bed IS NULL THEN
        UPDATE resources SET occupied_units = occupied_units + 1, last_updated = NOW()
        WHERE resource_type = 'bed';
    END IF;

    IF NEW.status = 'complete' AND OLD.status <> 'complete'
       AND OLD.assigned_bed IS NOT NULL THEN
        UPDATE resources
        SET occupied_units = GREATEST(occupied_units - 1, 0), last_updated = NOW()
        WHERE resource_type = 'bed';
    END IF;
END$

DELIMITER ;
""", language="sql")

    with st.expander("📢 evt_escalate_alerts — Escalate unresolved critical alerts after 10 min"):
        st.code("""
DELIMITER $

CREATE EVENT evt_escalate_alerts
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    UPDATE alerts
    SET escalated = TRUE
    WHERE severity    = 'critical'
      AND resolved_at IS NULL
      AND escalated   = FALSE
      AND TIMESTAMPDIFF(MINUTE, triggered_at, NOW()) >= 10;
END$

DELIMITER ;
""", language="sql")

    # ── Simulate trigger execution against MongoDB ──
    st.divider()
    st.markdown("### Simulate Trigger (MongoDB)")
    with st.form("trigger_sim"):
        visit_id   = st.text_input("Visit ID", value="ERV-2026-SIM01")
        system     = st.selectbox("Triage System", ["ESI", "CTAS", "MTS"])
        priority   = st.slider("Priority Level", 1, 5, 2)
        pain       = st.slider("Pain Score", 0, 10, 7)
        submitted  = st.form_submit_button("Insert Triage Record")

    if submitted:
        now = datetime.utcnow()
        # Upsert a visit if it doesn't exist
        _col("er_visits").update_one(
            {"visit_id": visit_id},
            {"$setOnInsert": {
                "visit_id": visit_id,
                "patient_id": "PT-SIM",
                "arrival_time": now,
                "chief_complaint": "Simulated visit",
                "status": "in_triage",
                "assigned_bed": None,
                "attending_doctor": "DR-SIM",
            }},
            upsert=True,
        )
        # Insert triage record
        _col("triage").insert_one({
            "visit_id":      visit_id,
            "triage_system": system,
            "priority_level": priority,
            "pain_score":    pain,
            "assessed_by":   "RN-SIM",
            "assessed_at":   now,
        })
        # Simulate trigger: auto-create alert for priority <= 2
        if priority <= 2:
            _col("alerts").insert_one({
                "visit_id":    visit_id,
                "alert_type":  f"{system} Level {priority} — Immediate attention required",
                "severity":    "critical" if priority == 1 else "warning",
                "triggered_at": now,
                "resolved_at": None,
                "resolved_by": None,
                "escalated":   False,
            })
            st.warning(f"⚡ Trigger fired: Alert created for {system} Level {priority}")
        else:
            st.success(f"✅ Triage record inserted for {visit_id} (no alert — priority {priority})")


# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────

def _output_tab():
    st.markdown("### Module Output — Live from MongoDB")
    now = datetime.utcnow()

    # ── Summary metrics ────────────────────────
    bed_doc       = _col("resources").find_one({"resource_type": "bed"}) or {}
    beds_occ      = bed_doc.get("occupied_units", 0)
    beds_total    = bed_doc.get("total_units", 1)
    active_alerts = _col("alerts").count_documents({"resolved_at": None})
    critical_cnt  = _col("alerts").count_documents({"severity": "critical", "resolved_at": None})
    warning_cnt   = active_alerts - critical_cnt

    wt_agg = list(_col("wait_times").aggregate([
        {"$group": {"_id": None,
                    "avg_d2d": {"$avg": "$door_to_doctor_min"},
                    "avg_los": {"$avg": "$length_of_stay_min"}}}
    ]))
    avg_d2d = round(wt_agg[0]["avg_d2d"], 1) if wt_agg else "N/A"
    avg_los = round(wt_agg[0]["avg_los"], 1) if wt_agg else "N/A"
    nedocs  = round((beds_occ / beds_total) * 85, 1)

    st.success("✅ Emergency Room Patient Alert System — Operational")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Live ER Status")
        occ_pct = beds_occ / beds_total * 100
        bed_status = "🔴 Critical" if occ_pct >= 90 else ("🟠 High" if occ_pct >= 75 else "🟢 Normal")
        st.info(f"🛏️ Beds: {beds_occ} / {beds_total} occupied  ({occ_pct:.1f}% — {bed_status})")
        st.warning(f"⚠️ Active Alerts: {active_alerts}  ({critical_cnt} critical, {warning_cnt} warning)")
        st.info(f"⏱️ Avg Door-to-Doctor: {avg_d2d} min")
        st.info(f"⏱️ Avg Length of Stay: {avg_los} min")
        nedocs_label = "Overcrowded" if nedocs >= 60 else "Normal"
        st.warning(f"📊 NEDOCS Score: {nedocs}  ({nedocs_label})")

        # ── Triage priority queue ──────────────
        st.markdown("#### Triage Priority Queue (Top 5)")
        pipeline = [
            {"$match": {"status": {"$in": ["waiting", "in_triage", "in_treatment"]}}},
            {"$lookup": {
                "from": "triage",
                "localField": "visit_id",
                "foreignField": "visit_id",
                "as": "t"
            }},
            {"$unwind": "$t"},
            {"$sort": {"t.priority_level": 1, "arrival_time": 1}},
            {"$limit": 5},
        ]
        queue = list(_col("er_visits").aggregate(pipeline))
        if queue:
            st.table({
                "Priority":   [f"{r['t']['triage_system']}-{r['t']['priority_level']}" for r in queue],
                "Complaint":  [r["chief_complaint"][:25] for r in queue],
                "Wait (min)": [int((now - r["arrival_time"]).total_seconds() / 60) for r in queue],
                "Bed":        [r.get("assigned_bed") or "Waiting" for r in queue],
            })

    with col2:
        st.markdown("#### Latest ERVisit Record")
        latest = _col("er_visits").find_one(sort=[("arrival_time", -1)])
        triage = _col("triage").find_one({"visit_id": latest["visit_id"]}) if latest else None
        wt     = _col("wait_times").find_one({"visit_id": latest["visit_id"]}) if latest else None

        if latest:
            record = {
                "visit_id":        latest["visit_id"],
                "patient_id":      latest["patient_id"],
                "arrival_time":    latest["arrival_time"].strftime("%Y-%m-%dT%H:%M:%S"),
                "chief_complaint": latest["chief_complaint"],
                "status":          latest["status"],
                "assigned_bed":    latest.get("assigned_bed"),
            }
            if triage:
                record["triage"] = {
                    "system":         triage["triage_system"],
                    "priority_level": triage["priority_level"],
                    "pain_score":     triage.get("pain_score"),
                    "vitals": {
                        "bp":         f"{triage.get('bp_systolic')}/{triage.get('bp_diastolic')} mmHg",
                        "heart_rate": f"{triage.get('heart_rate')} bpm",
                        "spo2":       f"{triage.get('spo2')}%",
                        "temperature":f"{triage.get('temperature')}°C",
                        "resp_rate":  f"{triage.get('resp_rate')}/min",
                    }
                }
            if wt:
                record["wait_times"] = {
                    "door_to_doctor_min":      wt.get("door_to_doctor_min"),
                    "door_to_disposition_min": wt.get("door_to_disposition_min"),
                    "length_of_stay_min":      wt.get("length_of_stay_min"),
                }
            st.json(record)

    st.divider()

    # ── Throughput ─────────────────────────────
    st.markdown("#### Throughput Report (Today by Hour)")
    tp_rows = list(_col("throughput").find({}, {"_id": 0}).sort("hour", 1))
    if tp_rows:
        st.table({
            "Hour":          [f"{r['hour']:02d}:00" for r in tp_rows],
            "Arrivals":      [r["arrivals"] for r in tp_rows],
            "Discharged":    [r["discharged"] for r in tp_rows],
            "Admitted":      [r["admitted"] for r in tp_rows],
            "Avg LOS (min)": [r["avg_los_min"] for r in tp_rows],
        })

    st.divider()

    # ── Resource utilisation ───────────────────
    st.markdown("#### Resource Utilisation")
    res_rows = list(_col("resources").find({}, {"_id": 0}))
    if res_rows:
        def util_status(r):
            pct = r["occupied_units"] / r["total_units"]
            return "🔴 Critical" if pct >= 0.90 else ("🟠 High" if pct >= 0.75 else "🟢 Normal")
        st.table({
            "Resource":    [r["resource_type"].capitalize() for r in res_rows],
            "Total":       [r["total_units"] for r in res_rows],
            "Occupied":    [r["occupied_units"] for r in res_rows],
            "Occupancy %": [f"{r['occupied_units']/r['total_units']*100:.1f}%" for r in res_rows],
            "Status":      [util_status(r) for r in res_rows],
        })

    st.divider()

    # ── Add new ER visit form ──────────────────
    st.markdown("#### Add New ER Visit")
    with st.form("new_visit_form"):
        c1, c2 = st.columns(2)
        with c1:
            patient_id  = st.text_input("Patient ID", value="PT-NEW")
            complaint   = st.text_input("Chief Complaint", value="Chest pain")
            triage_sys  = st.selectbox("Triage System", ["ESI", "CTAS", "MTS"])
            priority    = st.slider("Priority Level", 1, 5, 3)
        with c2:
            pain_score  = st.slider("Pain Score", 0, 10, 5)
            bp_sys      = st.number_input("BP Systolic", value=120)
            bp_dia      = st.number_input("BP Diastolic", value=80)
            heart_rate  = st.number_input("Heart Rate", value=80)
        submitted = st.form_submit_button("➕ Register Visit")

    if submitted:
        now2     = datetime.utcnow()
        visit_id = f"ERV-{now2.strftime('%Y%m%d%H%M%S')}"
        _col("er_visits").insert_one({
            "visit_id":        visit_id,
            "patient_id":      patient_id,
            "arrival_time":    now2,
            "chief_complaint": complaint,
            "departure_time":  None,
            "disposition":     None,
            "status":          "in_triage",
            "assigned_bed":    None,
            "attending_doctor": None,
        })
        _col("triage").insert_one({
            "visit_id":       visit_id,
            "triage_system":  triage_sys,
            "priority_level": priority,
            "pain_score":     pain_score,
            "bp_systolic":    int(bp_sys),
            "bp_diastolic":   int(bp_dia),
            "heart_rate":     int(heart_rate),
            "assessed_by":    "RN-FORM",
            "assessed_at":    now2,
        })
        # Simulate trigger
        if priority <= 2:
            _col("alerts").insert_one({
                "visit_id":    visit_id,
                "alert_type":  f"{triage_sys} Level {priority} — Immediate attention required",
                "severity":    "critical" if priority == 1 else "warning",
                "triggered_at": now2,
                "resolved_at": None,
                "resolved_by": None,
                "escalated":   False,
            })
            st.warning(f"⚡ Alert auto-created for {visit_id} (Priority {priority})")
        else:
            st.success(f"✅ Visit {visit_id} registered successfully.")
        st.rerun()
