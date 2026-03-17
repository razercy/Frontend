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


def module_e2_detail():
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
    st.markdown("### Live ER Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ER Visits Today", "142", delta="+18 vs yesterday")
    c2.metric("Active Alerts", "9", delta="+3", delta_color="inverse")
    c3.metric("Avg Door-to-Doctor", "22 min", delta="-4 min", delta_color="normal")
    c4.metric("NEDOCS Score", "68", help="60-100 = Overcrowded", delta_color="inverse")

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
        "Current Avg": ["22 min", "3h 41min", "5h 12min", "2h 58min"],
        "Status": ["✅ On Target", "✅ On Target", "✅ On Target", "✅ On Target"],
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
│    disposition       │        │    assessed_by (FK)      │
│    status            │        │    pain_score            │
└──────────────────────┘        │    notes                 │
          │ 1                   └─────────────────────────┘
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
│    resolved_by (FK)  │        └─────────────────────────┘
└──────────────────────┘
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
    st.image(
        "https://via.placeholder.com/900x420?text=ER+Diagram+-+Module+26+Emergency+Room+Alert",
        caption="Module 26 — Entity Relationship Diagram",
    )


# ─────────────────────────────────────────────
# TABLES
# ─────────────────────────────────────────────
def _tables_tab():
    st.markdown("### Database Tables")
    st.table({
        "Table": ["er_visits", "triage", "alerts", "resources", "wait_times"],
        "Primary Key": ["visit_id", "triage_id", "alert_id", "resource_id", "waittime_id"],
        "Records": [14200, 14180, 8900, 120, 13950],
        "Status": ["✅ Active"] * 5,
    })

    st.divider()
    st.markdown("#### DDL Schemas")

    with st.expander("er_visits"):
        st.code("""
CREATE TABLE er_visits (
    visit_id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id        INT NOT NULL,
    arrival_time      DATETIME NOT NULL DEFAULT NOW(),
    chief_complaint   TEXT NOT NULL,
    departure_time    DATETIME,
    disposition       ENUM('discharged','admitted','transferred','left_ama','expired'),
    status            ENUM('waiting','in_triage','in_treatment','boarding','complete')
                      NOT NULL DEFAULT 'waiting',
    assigned_bed      VARCHAR(10),
    attending_doctor  INT,
    FOREIGN KEY (patient_id)       REFERENCES patients(patient_id),
    FOREIGN KEY (attending_doctor) REFERENCES staff(staff_id)
);
""", language="sql")

    with st.expander("triage"):
        st.code("""
CREATE TABLE triage (
    triage_id         INT AUTO_INCREMENT PRIMARY KEY,
    visit_id          INT NOT NULL UNIQUE,
    triage_system     ENUM('ESI','CTAS','MTS') NOT NULL DEFAULT 'ESI',
    priority_level    TINYINT NOT NULL CHECK (priority_level BETWEEN 1 AND 5),
    pain_score        TINYINT CHECK (pain_score BETWEEN 0 AND 10),
    bp_systolic       SMALLINT,
    bp_diastolic      SMALLINT,
    heart_rate        SMALLINT,
    spo2              DECIMAL(5,2),
    temperature       DECIMAL(4,1),
    resp_rate         TINYINT,
    assessed_by       INT NOT NULL,
    assessed_at       DATETIME NOT NULL DEFAULT NOW(),
    notes             TEXT,
    FOREIGN KEY (visit_id)    REFERENCES er_visits(visit_id),
    FOREIGN KEY (assessed_by) REFERENCES staff(staff_id)
);
""", language="sql")

    with st.expander("alerts"):
        st.code("""
CREATE TABLE alerts (
    alert_id          INT AUTO_INCREMENT PRIMARY KEY,
    visit_id          INT NOT NULL,
    alert_type        VARCHAR(100) NOT NULL,
    severity          ENUM('info','warning','critical') NOT NULL,
    triggered_at      DATETIME NOT NULL DEFAULT NOW(),
    resolved_at       DATETIME,
    resolved_by       INT,
    escalated         BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (visit_id)    REFERENCES er_visits(visit_id),
    FOREIGN KEY (resolved_by) REFERENCES staff(staff_id)
);
""", language="sql")

    with st.expander("resources"):
        st.code("""
CREATE TABLE resources (
    resource_id       INT AUTO_INCREMENT PRIMARY KEY,
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
    waittime_id             INT AUTO_INCREMENT PRIMARY KEY,
    visit_id                INT NOT NULL UNIQUE,
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
    t.priority_level ASC,          -- lower level = higher urgency
    ev.arrival_time  ASC;          -- FIFO within same level
""",
        "Time Interval Calculations (Door-to-Doctor, LOS)": """
-- Calculate key ER time targets per visit
SELECT
    ev.visit_id,
    ev.arrival_time,
    ev.departure_time,
    TIMESTAMPDIFF(MINUTE, ev.arrival_time, t.assessed_at)   AS door_to_triage_min,
    wt.door_to_doctor_min,
    wt.door_to_disposition_min,
    wt.length_of_stay_min,
    CASE
        WHEN wt.door_to_doctor_min <= 30  THEN 'On Target'
        ELSE 'Breached'
    END AS door_to_doctor_status,
    CASE
        WHEN wt.length_of_stay_min <= 240 THEN 'On Target'
        ELSE 'Breached'
    END AS los_status
FROM er_visits ev
JOIN triage    t  ON ev.visit_id = t.visit_id
JOIN wait_times wt ON ev.visit_id = wt.visit_id
ORDER BY ev.arrival_time DESC
LIMIT 50;
""",
        "ER Crowding Index (NEDOCS Approximation)": """
-- Simplified NEDOCS crowding score approximation
-- NEDOCS = f(total patients, admitted boarders, longest wait, last bed time, vents)
SELECT
    COUNT(*)                                                AS total_er_patients,
    SUM(CASE WHEN ev.status = 'boarding' THEN 1 ELSE 0 END) AS admitted_boarders,
    MAX(TIMESTAMPDIFF(MINUTE, ev.arrival_time, NOW()))      AS longest_wait_min,
    (SELECT occupied_units FROM resources
     WHERE resource_type = 'bed' LIMIT 1)                  AS beds_occupied,
    (SELECT total_units   FROM resources
     WHERE resource_type = 'bed' LIMIT 1)                  AS beds_total,
    ROUND(
        (COUNT(*) / NULLIF(
            (SELECT total_units FROM resources WHERE resource_type='bed' LIMIT 1), 0)
        ) * 85, 1
    )                                                       AS nedocs_approx
FROM er_visits ev
WHERE ev.status NOT IN ('complete');
""",
        "Resource Utilisation & Prediction": """
-- Current resource utilisation with occupancy % and predicted shortage
SELECT
    resource_type,
    location,
    total_units,
    occupied_units,
    (total_units - occupied_units)                          AS available_units,
    ROUND(occupied_units / total_units * 100, 1)            AS occupancy_pct,
    CASE
        WHEN occupied_units / total_units >= 0.90 THEN '🔴 Critical'
        WHEN occupied_units / total_units >= 0.75 THEN '🟠 High'
        ELSE '🟢 Normal'
    END AS utilisation_status
FROM resources
ORDER BY occupancy_pct DESC;
""",
        "Throughput Report by Hour": """
-- ER patient throughput: arrivals and dispositions per hour (today)
SELECT
    HOUR(ev.arrival_time)                                   AS hour_of_day,
    COUNT(*)                                                AS total_arrivals,
    SUM(CASE WHEN ev.disposition = 'discharged' THEN 1 ELSE 0 END) AS discharged,
    SUM(CASE WHEN ev.disposition = 'admitted'   THEN 1 ELSE 0 END) AS admitted,
    ROUND(AVG(wt.length_of_stay_min), 1)                    AS avg_los_min
FROM er_visits ev
LEFT JOIN wait_times wt ON ev.visit_id = wt.visit_id
WHERE DATE(ev.arrival_time) = CURDATE()
GROUP BY HOUR(ev.arrival_time)
ORDER BY hour_of_day;
""",
        "Unresolved Critical Alerts": """
-- All unresolved critical alerts with time open
SELECT
    a.alert_id,
    ev.visit_id,
    ev.assigned_bed,
    a.alert_type,
    a.severity,
    a.triggered_at,
    TIMESTAMPDIFF(MINUTE, a.triggered_at, NOW())            AS minutes_open,
    a.escalated
FROM alerts a
JOIN er_visits ev ON a.visit_id = ev.visit_id
WHERE a.severity = 'critical'
  AND a.resolved_at IS NULL
ORDER BY a.triggered_at ASC;
""",
    }

    st.code(queries[sel], language="sql")

    if st.button("▶️ Execute Query", key="e2_exec"):
        st.success("Query executed successfully!")
        if sel == "Triage Priority Queue (Queue Management)":
            st.table({
                "Visit ID": [1021, 1034, 1019, 1041, 1055],
                "Chief Complaint": ["Chest pain", "Altered consciousness", "Abdominal pain", "Laceration", "Sore throat"],
                "System": ["ESI", "CTAS", "MTS", "ESI", "ESI"],
                "Priority": [1, 2, 3, 4, 5],
                "Wait (min)": [2, 8, 25, 40, 62],
                "Status": ["in_treatment", "in_triage", "waiting", "waiting", "waiting"],
            })
        elif sel == "Resource Utilisation & Prediction":
            st.table({
                "Resource": ["bed", "doctor", "nurse", "ventilator", "monitor"],
                "Total": [48, 12, 24, 8, 20],
                "Occupied": [43, 10, 19, 6, 15],
                "Available": [5, 2, 5, 2, 5],
                "Occupancy %": ["89.6%", "83.3%", "79.2%", "75.0%", "75.0%"],
                "Status": ["🔴 Critical", "🟠 High", "🟠 High", "🟢 Normal", "🟢 Normal"],
            })
        elif sel == "ER Crowding Index (NEDOCS Approximation)":
            st.table({
                "Total ER Patients": [43],
                "Admitted Boarders": [7],
                "Longest Wait (min)": [148],
                "Beds Occupied": [43],
                "Beds Total": [48],
                "NEDOCS Approx": [76.0],
            })
        else:
            st.info("Sample result set would appear here.")


# ─────────────────────────────────────────────
# TRIGGERS
# ─────────────────────────────────────────────
def _triggers_tab():
    st.markdown("### Database Triggers")

    with st.expander("🔔 trg_triage_alert — Fire alert on high-priority triage", expanded=True):
        st.code("""
DELIMITER $$

-- Automatically create an alert when a Level-1 or Level-2 triage is recorded
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
END$$

DELIMITER ;
""", language="sql")

    with st.expander("⏱️ trg_wait_time_log — Record time intervals on departure"):
        st.code("""
DELIMITER $$

-- Capture door-to-doctor, door-to-disposition, and LOS when visit closes
CREATE TRIGGER trg_wait_time_log
AFTER UPDATE ON er_visits
FOR EACH ROW
BEGIN
    DECLARE v_door_to_doc   SMALLINT;
    DECLARE v_door_to_disp  SMALLINT;
    DECLARE v_los           SMALLINT;

    IF NEW.status = 'complete' AND OLD.status <> 'complete' THEN
        -- Door-to-doctor: arrival → first triage assessment
        SELECT TIMESTAMPDIFF(MINUTE, NEW.arrival_time, MIN(assessed_at))
        INTO v_door_to_doc
        FROM triage WHERE visit_id = NEW.visit_id;

        -- Door-to-disposition & LOS: arrival → departure
        SET v_door_to_disp = TIMESTAMPDIFF(MINUTE, NEW.arrival_time, NEW.departure_time);
        SET v_los          = v_door_to_disp;

        INSERT INTO wait_times
            (visit_id, door_to_doctor_min, door_to_disposition_min, length_of_stay_min)
        VALUES
            (NEW.visit_id, v_door_to_doc, v_door_to_disp, v_los)
        ON DUPLICATE KEY UPDATE
            door_to_doctor_min      = v_door_to_doc,
            door_to_disposition_min = v_door_to_disp,
            length_of_stay_min      = v_los,
            recorded_at             = NOW();
    END IF;
END$$

DELIMITER ;
""", language="sql")

    with st.expander("🛏️ trg_resource_update — Adjust bed count on admission/discharge"):
        st.code("""
DELIMITER $$

-- Keep resource occupancy in sync when a patient is assigned or leaves a bed
CREATE TRIGGER trg_resource_update
AFTER UPDATE ON er_visits
FOR EACH ROW
BEGIN
    -- Patient assigned to a bed
    IF NEW.assigned_bed IS NOT NULL AND OLD.assigned_bed IS NULL THEN
        UPDATE resources
        SET occupied_units = occupied_units + 1,
            last_updated   = NOW()
        WHERE resource_type = 'bed';
    END IF;

    -- Patient left (discharged / admitted / transferred)
    IF NEW.status = 'complete' AND OLD.status <> 'complete'
       AND OLD.assigned_bed IS NOT NULL THEN
        UPDATE resources
        SET occupied_units = GREATEST(occupied_units - 1, 0),
            last_updated   = NOW()
        WHERE resource_type = 'bed';
    END IF;
END$$

DELIMITER ;
""", language="sql")

    with st.expander("📢 trg_alert_escalate — Escalate unresolved critical alerts after 10 min"):
        st.code("""
DELIMITER $$

-- Mark alert as escalated if still unresolved after 10 minutes
-- (Called by a scheduled event every minute)
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
END$$

DELIMITER ;
""", language="sql")


# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────
def _output_tab():
    st.markdown("### Module Output")
    st.success("✅ Emergency Room Patient Alert System — Operational")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Live ER Status")
        st.info("🛏️ Beds: 43 / 48 occupied  (89.6% — 🔴 Critical)")
        st.warning("⚠️ Active Alerts: 9  (4 critical, 5 warning)")
        st.info("⏱️ Avg Door-to-Doctor: 22 min  ✅")
        st.info("⏱️ Avg Length of Stay: 3h 12min  ✅")
        st.warning("📊 NEDOCS Score: 76  (Overcrowded)")

        st.markdown("#### Triage Priority Queue (Top 5)")
        st.table({
            "Priority": ["ESI-1", "CTAS-2", "MTS-Urgent", "ESI-3", "ESI-4"],
            "Complaint": ["Chest pain", "Altered GCS", "Abd. pain", "Fever + rash", "Ankle sprain"],
            "Wait (min)": [2, 8, 25, 38, 55],
            "Bed": ["ER-02", "ER-07", "Waiting", "Waiting", "Waiting"],
        })

    with col2:
        st.markdown("#### Sample ERVisit Record")
        st.json({
            "visit_id": "ERV-2026-01847",
            "patient_id": "[Patient ID]",
            "arrival_time": "2026-03-18T09:42:00",
            "chief_complaint": "Chest pain with shortness of breath",
            "status": "in_treatment",
            "assigned_bed": "ER-06",
            "triage": {
                "system": "ESI",
                "priority_level": 2,
                "pain_score": 8,
                "vitals": {
                    "bp": "158/96 mmHg",
                    "heart_rate": "112 bpm",
                    "spo2": "94%",
                    "temperature": "37.8°C",
                    "resp_rate": "22/min"
                }
            },
            "wait_times": {
                "door_to_doctor_min": 18,
                "door_to_disposition_min": None,
                "length_of_stay_min": None
            }
        })

    st.divider()
    st.markdown("#### Throughput Report (Today by Hour)")
    st.table({
        "Hour": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"],
        "Arrivals": [8, 14, 18, 22, 16, 19, 21],
        "Discharged": [5, 10, 12, 15, 11, 14, 16],
        "Admitted": [2, 3, 4, 5, 3, 4, 4],
        "Avg LOS (min)": [185, 192, 198, 204, 188, 195, 201],
    })

    st.divider()
    st.markdown("#### Resource Utilisation")
    st.table({
        "Resource": ["Beds", "Doctors", "Nurses", "Ventilators", "Monitors"],
        "Total": [48, 12, 24, 8, 20],
        "Occupied": [43, 10, 19, 6, 15],
        "Occupancy %": ["89.6%", "83.3%", "79.2%", "75.0%", "75.0%"],
        "Status": ["🔴 Critical", "🟠 High", "🟠 High", "🟢 Normal", "🟢 Normal"],
    })
