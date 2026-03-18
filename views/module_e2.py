"""
Module 26: Emergency Room Patient Alert System
Category E: ICU & Real-Time Monitoring

Schema (per entity-relationship-diagram.md):
  ER_VISIT     : VisitID PK, LogID FK, AlertID FK, TriageID FK, ResourceID FK, ArrivalTime
  WAIT_TIME_LOG: LogID PK, Stage, Duration
  ALERT        : AlertID PK, Type, Status
  TRIAGE       : TriageID PK, Score, System
  RESOURCE     : ResourceID PK, Type

Relationships:
  WAIT_TIME_LOG ||--o{ ER_VISIT  : Tracks
  ER_VISIT      ||--o{ ALERT     : Triggers
  ER_VISIT      ||--|| TRIAGE    : Has
  ER_VISIT      }o--o{ RESOURCE  : Utilizes
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


def _next_id(col_name: str) -> int:
    """Simple auto-increment using a counters collection."""
    result = _col("counters").find_one_and_update(
        {"_id": col_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]


def _seed_if_empty():
    """Seed MongoDB collections with sample data aligned to the ER diagram schema."""
    if _col("er_visits").count_documents({}) > 0:
        return

    now = datetime.utcnow()

    # Drop all collections for a clean seed
    for c in ["er_visits", "triage", "alerts", "wait_time_log", "resources",
              "visit_resources", "counters", "throughput"]:
        _col(c).drop()

    # ── RESOURCE ──────────────────────────────
    resource_types = ["bed", "doctor", "nurse", "ventilator", "monitor"]
    resource_ids = {}
    for rtype in resource_types:
        rid = _next_id("resource")
        _col("resources").insert_one({"resource_id": rid, "type": rtype})
        resource_ids[rtype] = rid

    # ── Seed visits ───────────────────────────
    complaints = [
        ("Chest pain with shortness of breath", 9,  "ESI"),
        ("Altered consciousness",               8,  "CTAS"),
        ("Abdominal pain",                      6,  "MTS"),
        ("Fever and rash",                      5,  "ESI"),
        ("Ankle sprain",                        3,  "ESI"),
        ("Laceration on forearm",               4,  "ESI"),
        ("Sore throat",                         2,  "ESI"),
        ("Headache",                            5,  "MTS"),
        ("Difficulty breathing",                8,  "ESI"),
        ("Back pain",                           4,  "CTAS"),
    ]
    stages = ["Waiting", "Triage", "Treatment", "Boarding", "Discharge"]
    alert_statuses = ["Open", "Resolved"]

    for i, (complaint, score, system) in enumerate(complaints):
        arrival = now - timedelta(minutes=random.randint(5, 180))
        stage   = stages[i % len(stages)]

        # TRIAGE
        triage_id = _next_id("triage")
        _col("triage").insert_one({
            "triage_id": triage_id,
            "score":     score,
            "system":    system,
        })

        # ALERT (only for high-score patients)
        alert_id = None
        if score >= 8:
            alert_id = _next_id("alert")
            _col("alerts").insert_one({
                "alert_id": alert_id,
                "type":     f"{system} Score {score} — Immediate attention required",
                "status":   alert_statuses[i % 2],
            })

        # WAIT_TIME_LOG
        log_id = _next_id("log")
        duration = random.randint(10, 180)
        _col("wait_time_log").insert_one({
            "log_id":   log_id,
            "stage":    stage,
            "duration": duration,
        })

        # ER_VISIT (holds all FKs)
        visit_id = _next_id("visit")
        assigned_resource = resource_ids["bed"]
        _col("er_visits").insert_one({
            "visit_id":    visit_id,
            "log_id":      log_id,
            "alert_id":    alert_id,
            "triage_id":   triage_id,
            "resource_id": assigned_resource,
            "arrival_time": arrival,
            "chief_complaint": complaint,
            "stage":       stage,
        })

        # VISIT_RESOURCES (many-to-many junction)
        assigned = random.sample(list(resource_ids.values()), k=random.randint(1, 3))
        for rid in assigned:
            _col("visit_resources").insert_one({
                "visit_id":   visit_id,
                "resource_id": rid,
            })

    # ── Throughput (hourly buckets) ────────────
    for h in range(8, 15):
        arrivals   = random.randint(8, 22)
        discharged = int(arrivals * random.uniform(0.6, 0.8))
        admitted   = max(arrivals - discharged - random.randint(0, 2), 0)
        _col("throughput").insert_one({
            "hour": h, "arrivals": arrivals,
            "discharged": discharged, "admitted": admitted,
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
        st.success("1️⃣ ER_VISIT — arrival time, FK references to all entities")
        st.success("2️⃣ TRIAGE — score (0-10), triage system (ESI/CTAS/MTS)")
        st.success("3️⃣ ALERT — type description, open/resolved status")
        st.success("4️⃣ RESOURCE — resource type (bed, doctor, nurse…)")
        st.success("5️⃣ WAIT_TIME_LOG — stage name, duration in minutes")

    with col2:
        st.markdown("### Output Entities")
        st.success("1️⃣ Triage Priority Queue (ranked by score)")
        st.success("2️⃣ Active Alert Notifications (Open alerts)")
        st.success("3️⃣ Resource Utilisation Report")
        st.success("4️⃣ Wait-Time & Throughput Dashboard")
        st.success("5️⃣ Stage-by-Stage Duration Breakdown")

    st.divider()
    st.markdown("### Live ER Metrics")
    now = datetime.utcnow()

    total_visits  = _col("er_visits").count_documents({"stage": {"$ne": "Discharge"}})
    active_alerts = _col("alerts").count_documents({"status": "Open"})

    wt_agg = list(_col("wait_time_log").aggregate(
        [{"$group": {"_id": None, "avg": {"$avg": "$duration"}}}]
    ))
    avg_duration = round(wt_agg[0]["avg"], 1) if wt_agg else "N/A"

    total_resources = _col("resources").count_documents({})
    assigned_resources = _col("visit_resources").count_documents({})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ER Visits (Active)", total_visits)
    c2.metric("Open Alerts", active_alerts, delta_color="inverse")
    c3.metric("Avg Stage Duration", f"{avg_duration} min")
    c4.metric("Resource Assignments", assigned_resources)

    st.divider()
    st.markdown("### Triage Systems Supported")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("**ESI (Emergency Severity Index)**")
        st.error("Score 9-10 — Immediate")
        st.warning("Score 7-8 — Emergent")
        st.info("Score 5-6 — Urgent")
        st.success("Score 3-4 — Less Urgent")
        st.success("Score 1-2 — Non-Urgent")
    with t2:
        st.markdown("**CTAS (Canadian Triage & Acuity Scale)**")
        st.error("Score 9-10 — Resuscitation")
        st.warning("Score 7-8 — Emergent")
        st.info("Score 5-6 — Urgent")
        st.success("Score 3-4 — Less Urgent")
        st.success("Score 1-2 — Non-Urgent")
    with t3:
        st.markdown("**MTS (Manchester Triage System)**")
        st.error("🔴 Score 9-10 — Immediate")
        st.warning("🟠 Score 7-8 — Very Urgent")
        st.info("🟡 Score 5-6 — Urgent")
        st.success("🟢 Score 3-4 — Standard")
        st.success("⚪ Score 1-2 — Non-Urgent")

    st.divider()
    st.markdown("### Key Time Targets")
    st.table({
        "Stage":    ["Waiting", "Triage", "Treatment", "Boarding", "Discharge"],
        "Target (min)": ["≤ 30", "≤ 15", "≤ 120", "≤ 60", "≤ 30"],
    })


# ─────────────────────────────────────────────
# ER DIAGRAM
# ─────────────────────────────────────────────

def _er_diagram_tab():
    st.markdown("### Entity Relationship Diagram")
    st.code("""
┌──────────────────────────┐       ┌──────────────────────┐
│        ER_VISIT          │       │    WAIT_TIME_LOG      │
├──────────────────────────┤       ├──────────────────────┤
│ PK VisitID               │       │ PK LogID             │
│ FK LogID      ───────────┼──────►│    Stage             │
│ FK AlertID               │       │    Duration          │
│ FK TriageID              │       └──────────────────────┘
│ FK ResourceID            │
│    ArrivalTime           │       ┌──────────────────────┐
└──────────────────────────┘       │       ALERT          │
          │                        ├──────────────────────┤
          │ FK AlertID ────────────►│ PK AlertID          │
          │                        │    Type              │
          │                        │    Status            │
          │                        └──────────────────────┘
          │
          │ FK TriageID ──────────►┌──────────────────────┐
          │                        │       TRIAGE         │
          │                        ├──────────────────────┤
          │                        │ PK TriageID          │
          │                        │    Score             │
          │                        │    System            │
          │                        └──────────────────────┘
          │
          │ FK ResourceID ────────►┌──────────────────────┐
          │  (+ visit_resources    │      RESOURCE        │
          │   junction for M:N)    ├──────────────────────┤
          └───────────────────────►│ PK ResourceID        │
                                   │    Type              │
                                   └──────────────────────┘
""", language="text")
    st.markdown("**Relationships**")
    st.table({
        "From":       ["WAIT_TIME_LOG", "ER_VISIT", "ER_VISIT", "ER_VISIT"],
        "To":         ["ER_VISIT",      "ALERT",    "TRIAGE",   "RESOURCE"],
        "Cardinality":["1 : Many",      "1 : Many", "1 : 1",    "Many : Many"],
        "Label":      ["Tracks",        "Triggers", "Has",      "Utilizes"],
    })


# ─────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────

def _tables_tab():
    st.markdown("### Database Collections")

    collections = {
        "er_visits":       "ER_VISIT",
        "triage":          "TRIAGE",
        "alerts":          "ALERT",
        "resources":       "RESOURCE",
        "wait_time_log":   "WAIT_TIME_LOG",
        "visit_resources": "VISIT_RESOURCES (junction)",
        "throughput":      "Throughput",
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
    st.markdown("#### DDL Schemas")

    with st.expander("ER_VISIT"):
        st.code("""
CREATE TABLE ER_VISIT (
    VisitID    INT PRIMARY KEY AUTO_INCREMENT,
    LogID      INT NOT NULL,
    AlertID    INT,
    TriageID   INT NOT NULL,
    ResourceID INT NOT NULL,
    ArrivalTime DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (LogID)      REFERENCES WAIT_TIME_LOG(LogID),
    FOREIGN KEY (AlertID)    REFERENCES ALERT(AlertID),
    FOREIGN KEY (TriageID)   REFERENCES TRIAGE(TriageID),
    FOREIGN KEY (ResourceID) REFERENCES RESOURCE(ResourceID)
);
""", language="sql")

    with st.expander("WAIT_TIME_LOG"):
        st.code("""
CREATE TABLE WAIT_TIME_LOG (
    LogID    INT PRIMARY KEY AUTO_INCREMENT,
    Stage    VARCHAR(50) NOT NULL,
    Duration INT NOT NULL COMMENT 'Duration in minutes'
);
""", language="sql")

    with st.expander("ALERT"):
        st.code("""
CREATE TABLE ALERT (
    AlertID INT PRIMARY KEY AUTO_INCREMENT,
    Type    VARCHAR(100) NOT NULL,
    Status  ENUM('Open', 'Resolved') NOT NULL DEFAULT 'Open'
);
""", language="sql")

    with st.expander("TRIAGE"):
        st.code("""
CREATE TABLE TRIAGE (
    TriageID INT PRIMARY KEY AUTO_INCREMENT,
    Score    TINYINT NOT NULL CHECK (Score BETWEEN 1 AND 10),
    System   ENUM('ESI', 'CTAS', 'MTS') NOT NULL
);
""", language="sql")

    with st.expander("RESOURCE"):
        st.code("""
CREATE TABLE RESOURCE (
    ResourceID INT PRIMARY KEY AUTO_INCREMENT,
    Type       VARCHAR(50) NOT NULL
);
""", language="sql")

    with st.expander("VISIT_RESOURCES (M:N junction)"):
        st.code("""
CREATE TABLE VISIT_RESOURCES (
    VisitID    INT NOT NULL,
    ResourceID INT NOT NULL,
    PRIMARY KEY (VisitID, ResourceID),
    FOREIGN KEY (VisitID)    REFERENCES ER_VISIT(VisitID),
    FOREIGN KEY (ResourceID) REFERENCES RESOURCE(ResourceID)
);
""", language="sql")


# ─────────────────────────────────────────────
# SQL QUERIES
# ─────────────────────────────────────────────

def _sql_tab():
    st.markdown("### Sample SQL Queries")

    query_options = [
        "Triage Priority Queue (by Score)",
        "Wait Time by Stage",
        "Open Alerts",
        "Resource Utilisation per Visit",
        "Throughput Report by Hour",
    ]
    sel = st.selectbox("Select a query", query_options, key="e2_query_sel")

    queries = {
        "Triage Priority Queue (by Score)": """
-- Patients ranked by triage score (highest = most urgent), then arrival time
SELECT
    ev.VisitID,
    ev.ArrivalTime,
    t.System          AS triage_system,
    t.Score           AS triage_score,
    TIMESTAMPDIFF(MINUTE, ev.ArrivalTime, NOW()) AS wait_min,
    wl.Stage          AS current_stage
FROM ER_VISIT ev
JOIN TRIAGE       t  ON ev.TriageID = t.TriageID
JOIN WAIT_TIME_LOG wl ON ev.LogID   = wl.LogID
WHERE wl.Stage <> 'Discharge'
ORDER BY t.Score DESC, ev.ArrivalTime ASC;
""",
        "Wait Time by Stage": """
-- Average and total duration per stage
SELECT
    Stage,
    COUNT(*)          AS visit_count,
    AVG(Duration)     AS avg_duration_min,
    MAX(Duration)     AS max_duration_min
FROM WAIT_TIME_LOG
GROUP BY Stage
ORDER BY avg_duration_min DESC;
""",
        "Open Alerts": """
-- All unresolved alerts with their associated visit
SELECT
    a.AlertID,
    a.Type,
    a.Status,
    ev.VisitID,
    ev.ArrivalTime,
    t.Score,
    t.System
FROM ALERT a
JOIN ER_VISIT ev ON a.AlertID = ev.AlertID
JOIN TRIAGE   t  ON ev.TriageID = t.TriageID
WHERE a.Status = 'Open'
ORDER BY t.Score DESC;
""",
        "Resource Utilisation per Visit": """
-- Resources assigned to each active visit (M:N join)
SELECT
    ev.VisitID,
    ev.ArrivalTime,
    GROUP_CONCAT(r.Type ORDER BY r.Type SEPARATOR ', ') AS resources_assigned,
    COUNT(r.ResourceID) AS resource_count
FROM ER_VISIT ev
JOIN VISIT_RESOURCES vr ON ev.VisitID    = vr.VisitID
JOIN RESOURCE        r  ON vr.ResourceID = r.ResourceID
GROUP BY ev.VisitID, ev.ArrivalTime
ORDER BY resource_count DESC;
""",
        "Throughput Report by Hour": """
SELECT
    hour                                    AS hour_of_day,
    arrivals,
    discharged,
    admitted,
    avg_los_min
FROM throughput
ORDER BY hour;
""",
    }

    st.code(queries[sel], language="sql")

    if st.button("▶️ Execute Query", key="e2_exec"):
        st.success("Query executed — results from MongoDB:")
        now = datetime.utcnow()

        if sel == "Triage Priority Queue (by Score)":
            pipeline = [
                {"$lookup": {"from": "triage",        "localField": "triage_id",   "foreignField": "triage_id",   "as": "t"}},
                {"$lookup": {"from": "wait_time_log", "localField": "log_id",      "foreignField": "log_id",      "as": "wl"}},
                {"$unwind": "$t"},
                {"$unwind": "$wl"},
                {"$match": {"wl.stage": {"$ne": "Discharge"}}},
                {"$sort": {"t.score": -1, "arrival_time": 1}},
                {"$limit": 10},
            ]
            rows = list(_col("er_visits").aggregate(pipeline))
            if rows:
                st.table({
                    "Visit ID":    [r["visit_id"] for r in rows],
                    "System":      [r["t"]["system"] for r in rows],
                    "Score":       [r["t"]["score"] for r in rows],
                    "Wait (min)":  [int((now - r["arrival_time"]).total_seconds() / 60) for r in rows],
                    "Stage":       [r["wl"]["stage"] for r in rows],
                })

        elif sel == "Wait Time by Stage":
            pipeline = [
                {"$group": {"_id": "$stage",
                            "visit_count":    {"$sum": 1},
                            "avg_duration":   {"$avg": "$duration"},
                            "max_duration":   {"$max": "$duration"}}},
                {"$sort": {"avg_duration": -1}},
            ]
            rows = list(_col("wait_time_log").aggregate(pipeline))
            if rows:
                st.table({
                    "Stage":           [r["_id"] for r in rows],
                    "Visit Count":     [r["visit_count"] for r in rows],
                    "Avg Duration":    [round(r["avg_duration"], 1) for r in rows],
                    "Max Duration":    [r["max_duration"] for r in rows],
                })

        elif sel == "Open Alerts":
            pipeline = [
                {"$match": {"status": "Open"}},
                {"$lookup": {"from": "er_visits", "localField": "alert_id", "foreignField": "alert_id", "as": "ev"}},
                {"$unwind": {"path": "$ev", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {"from": "triage", "localField": "ev.triage_id", "foreignField": "triage_id", "as": "t"}},
                {"$unwind": {"path": "$t", "preserveNullAndEmptyArrays": True}},
                {"$sort": {"t.score": -1}},
            ]
            rows = list(_col("alerts").aggregate(pipeline))
            if rows:
                st.table({
                    "Alert ID":  [r["alert_id"] for r in rows],
                    "Type":      [r["type"][:40] for r in rows],
                    "Status":    [r["status"] for r in rows],
                    "Score":     [r.get("t", {}).get("score", "N/A") for r in rows],
                    "System":    [r.get("t", {}).get("system", "N/A") for r in rows],
                })
            else:
                st.info("No open alerts.")

        elif sel == "Resource Utilisation per Visit":
            pipeline = [
                {"$lookup": {"from": "resources", "localField": "resource_id", "foreignField": "resource_id", "as": "r"}},
                {"$unwind": "$r"},
                {"$limit": 10},
            ]
            rows = list(_col("er_visits").aggregate(pipeline))
            if rows:
                st.table({
                    "Visit ID":  [r["visit_id"] for r in rows],
                    "Resource":  [r["r"]["type"] for r in rows],
                    "Stage":     [r.get("stage", "N/A") for r in rows],
                })

        elif sel == "Throughput Report by Hour":
            rows = list(_col("throughput").find({}, {"_id": 0}).sort("hour", 1))
            if rows:
                st.table({
                    "Hour":          [f"{r['hour']:02d}:00" for r in rows],
                    "Arrivals":      [r["arrivals"] for r in rows],
                    "Discharged":    [r["discharged"] for r in rows],
                    "Admitted":      [r["admitted"] for r in rows],
                    "Avg LOS (min)": [r["avg_los_min"] for r in rows],
                })


# ─────────────────────────────────────────────
# TRIGGERS
# ─────────────────────────────────────────────

def _triggers_tab():
    st.markdown("### Database Triggers")

    with st.expander("🔔 trg_triage_alert — Fire alert when triage score ≥ 8", expanded=True):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_triage_alert
AFTER INSERT ON ER_VISIT
FOR EACH ROW
BEGIN
    DECLARE v_score TINYINT;
    DECLARE v_system VARCHAR(10);
    DECLARE v_alert_id INT;

    SELECT Score, System INTO v_score, v_system
    FROM TRIAGE WHERE TriageID = NEW.TriageID;

    IF v_score >= 8 THEN
        INSERT INTO ALERT (Type, Status)
        VALUES (
            CONCAT(v_system, ' Score ', v_score, ' — Immediate attention required'),
            'Open'
        );
        SET v_alert_id = LAST_INSERT_ID();

        UPDATE ER_VISIT SET AlertID = v_alert_id WHERE VisitID = NEW.VisitID;
    END IF;
END$

DELIMITER ;
""", language="sql")

    with st.expander("⏱️ trg_stage_log — Record wait time log on stage change"):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_stage_log
AFTER UPDATE ON ER_VISIT
FOR EACH ROW
BEGIN
    DECLARE v_duration INT;

    IF NEW.LogID <> OLD.LogID OR OLD.LogID IS NULL THEN
        -- Duration is managed externally; trigger ensures log exists
        INSERT IGNORE INTO WAIT_TIME_LOG (LogID, Stage, Duration)
        VALUES (NEW.LogID, 'Waiting', 0);
    END IF;
END$

DELIMITER ;
""", language="sql")

    with st.expander("📢 trg_alert_resolve — Auto-resolve alert when visit reaches Discharge"):
        st.code("""
DELIMITER $

CREATE TRIGGER trg_alert_resolve
AFTER UPDATE ON WAIT_TIME_LOG
FOR EACH ROW
BEGIN
    IF NEW.Stage = 'Discharge' AND OLD.Stage <> 'Discharge' THEN
        UPDATE ALERT a
        JOIN ER_VISIT ev ON ev.AlertID = a.AlertID
        JOIN WAIT_TIME_LOG wl ON wl.LogID = ev.LogID
        SET a.Status = 'Resolved'
        WHERE wl.LogID = NEW.LogID AND a.Status = 'Open';
    END IF;
END$

DELIMITER ;
""", language="sql")

    # ── Simulate trigger ──────────────────────
    st.divider()
    st.markdown("### Simulate Trigger (MongoDB)")
    with st.form("trigger_sim"):
        system   = st.selectbox("Triage System", ["ESI", "CTAS", "MTS"])
        score    = st.slider("Triage Score", 1, 10, 8)
        stage    = st.selectbox("Initial Stage", ["Waiting", "Triage", "Treatment", "Boarding"])
        duration = st.number_input("Stage Duration (min)", value=20, min_value=1)
        submitted = st.form_submit_button("Insert Visit Record")

    if submitted:
        now = datetime.utcnow()

        triage_id = _next_id("triage")
        _col("triage").insert_one({"triage_id": triage_id, "score": score, "system": system})

        log_id = _next_id("log")
        _col("wait_time_log").insert_one({"log_id": log_id, "stage": stage, "duration": int(duration)})

        alert_id = None
        if score >= 8:
            alert_id = _next_id("alert")
            _col("alerts").insert_one({
                "alert_id": alert_id,
                "type":     f"{system} Score {score} — Immediate attention required",
                "status":   "Open",
            })

        resource = _col("resources").find_one()
        resource_id = resource["resource_id"] if resource else 1

        visit_id = _next_id("visit")
        _col("er_visits").insert_one({
            "visit_id":    visit_id,
            "log_id":      log_id,
            "alert_id":    alert_id,
            "triage_id":   triage_id,
            "resource_id": resource_id,
            "arrival_time": now,
            "stage":       stage,
        })

        if score >= 8:
            st.warning(f"⚡ Trigger fired: Alert created for Visit {visit_id} ({system} Score {score})")
        else:
            st.success(f"✅ Visit {visit_id} registered (no alert — score {score})")


# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────

def _output_tab():
    st.markdown("### Module Output — Live from MongoDB")
    now = datetime.utcnow()

    total_visits  = _col("er_visits").count_documents({"stage": {"$ne": "Discharge"}})
    open_alerts   = _col("alerts").count_documents({"status": "Open"})
    total_resources = _col("resources").count_documents({})

    wt_agg = list(_col("wait_time_log").aggregate(
        [{"$group": {"_id": None, "avg": {"$avg": "$duration"}}}]
    ))
    avg_dur = round(wt_agg[0]["avg"], 1) if wt_agg else "N/A"

    st.success("✅ Emergency Room Patient Alert System — Operational")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Live ER Status")
        st.info(f"🏥 Active Visits: {total_visits}")
        st.warning(f"⚠️ Open Alerts: {open_alerts}")
        st.info(f"⏱️ Avg Stage Duration: {avg_dur} min")
        st.info(f"🔧 Resource Types: {total_resources}")

        st.markdown("#### Triage Priority Queue (Top 5)")
        pipeline = [
            {"$lookup": {"from": "triage",        "localField": "triage_id", "foreignField": "triage_id", "as": "t"}},
            {"$lookup": {"from": "wait_time_log", "localField": "log_id",    "foreignField": "log_id",    "as": "wl"}},
            {"$unwind": "$t"},
            {"$unwind": "$wl"},
            {"$match": {"wl.stage": {"$ne": "Discharge"}}},
            {"$sort": {"t.score": -1, "arrival_time": 1}},
            {"$limit": 5},
        ]
        queue = list(_col("er_visits").aggregate(pipeline))
        if queue:
            st.table({
                "Visit ID":   [r["visit_id"] for r in queue],
                "System":     [r["t"]["system"] for r in queue],
                "Score":      [r["t"]["score"] for r in queue],
                "Stage":      [r["wl"]["stage"] for r in queue],
                "Wait (min)": [int((now - r["arrival_time"]).total_seconds() / 60) for r in queue],
            })

    with col2:
        st.markdown("#### Latest ER_VISIT Record")
        latest = _col("er_visits").find_one(sort=[("arrival_time", -1)])
        if latest:
            triage   = _col("triage").find_one({"triage_id": latest["triage_id"]})
            log      = _col("wait_time_log").find_one({"log_id": latest["log_id"]})
            alert    = _col("alerts").find_one({"alert_id": latest.get("alert_id")}) if latest.get("alert_id") else None
            resource = _col("resources").find_one({"resource_id": latest["resource_id"]})

            record = {
                "visit_id":     latest["visit_id"],
                "arrival_time": latest["arrival_time"].strftime("%Y-%m-%dT%H:%M:%S"),
                "stage":        latest.get("stage"),
                "triage": {"score": triage["score"], "system": triage["system"]} if triage else None,
                "wait_time_log": {"stage": log["stage"], "duration_min": log["duration"]} if log else None,
                "alert": {"type": alert["type"], "status": alert["status"]} if alert else None,
                "resource": {"type": resource["type"]} if resource else None,
            }
            st.json(record)

    st.divider()

    st.markdown("#### Wait Time by Stage")
    stage_agg = list(_col("wait_time_log").aggregate([
        {"$group": {"_id": "$stage", "avg": {"$avg": "$duration"}, "count": {"$sum": 1}}},
        {"$sort": {"avg": -1}},
    ]))
    if stage_agg:
        st.table({
            "Stage":        [r["_id"] for r in stage_agg],
            "Visits":       [r["count"] for r in stage_agg],
            "Avg Duration": [round(r["avg"], 1) for r in stage_agg],
        })

    st.divider()

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

    st.markdown("#### Add New ER Visit")
    with st.form("new_visit_form"):
        c1, c2 = st.columns(2)
        with c1:
            triage_sys = st.selectbox("Triage System", ["ESI", "CTAS", "MTS"])
            score      = st.slider("Triage Score", 1, 10, 5)
            stage      = st.selectbox("Initial Stage", ["Waiting", "Triage", "Treatment", "Boarding"])
        with c2:
            duration   = st.number_input("Stage Duration (min)", value=15, min_value=1)
            res_type   = st.selectbox("Primary Resource", ["bed", "doctor", "nurse", "ventilator", "monitor"])
        submitted = st.form_submit_button("➕ Register Visit")

    if submitted:
        now2 = datetime.utcnow()

        triage_id = _next_id("triage")
        _col("triage").insert_one({"triage_id": triage_id, "score": score, "system": triage_sys})

        log_id = _next_id("log")
        _col("wait_time_log").insert_one({"log_id": log_id, "stage": stage, "duration": int(duration)})

        # Ensure resource exists
        resource = _col("resources").find_one({"type": res_type})
        if not resource:
            rid = _next_id("resource")
            _col("resources").insert_one({"resource_id": rid, "type": res_type})
            resource_id = rid
        else:
            resource_id = resource["resource_id"]

        alert_id = None
        if score >= 8:
            alert_id = _next_id("alert")
            _col("alerts").insert_one({
                "alert_id": alert_id,
                "type":     f"{triage_sys} Score {score} — Immediate attention required",
                "status":   "Open",
            })

        visit_id = _next_id("visit")
        _col("er_visits").insert_one({
            "visit_id":    visit_id,
            "log_id":      log_id,
            "alert_id":    alert_id,
            "triage_id":   triage_id,
            "resource_id": resource_id,
            "arrival_time": now2,
            "stage":       stage,
        })
        _col("visit_resources").insert_one({"visit_id": visit_id, "resource_id": resource_id})

        if score >= 8:
            st.warning(f"⚡ Alert auto-created for Visit {visit_id} (Score {score})")
        else:
            st.success(f"✅ Visit {visit_id} registered successfully.")
        st.rerun()
