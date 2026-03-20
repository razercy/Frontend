"""
Module 26: Emergency Room Patient Alert System
Category E: ICU & Real-Time Monitoring

Entities    : PATIENT, ER_VISIT, WAIT_TIME_LOG, ALERT, TRIAGE, RESOURCE
Triage      : ESI, CTAS, MTS
Time Targets: Door-to-doctor, Door-to-disposition, Length of stay
Features    : Crowding indices, Resource prediction, Flow optimization
Backend     : MongoDB (via db.py)
"""
import streamlit as st
from datetime import datetime, timezone
from db import get_collection

# ── collection handles ──────────────────────────────────────────────────────
def _col(name):
    return get_collection(name)


def module_e2_detail():
    st.markdown("Category E > ICU & Real-Time Monitoring > Module 26")
    st.markdown("# Emergency Room Patient Alert System")
    st.markdown(
        "*ER triage priority database, time-sensitive condition alerts, "
        "resource allocation optimization, and wait-time / throughput reporting.*"
    )

    tab = st.radio(
        "",
        ["🏠 Home", "🔗 ER Diagram", "🗺️ DFD", "📋 Collections", "🔍 Query", "⚡ Triggers", "🔌 API", "📊 Output"],
        horizontal=True,
        key="e2_tabs",
    )
    st.divider()

    if tab == "🏠 Home":
        _home_tab()
    elif tab == "🔗 ER Diagram":
        _er_diagram_tab()
    elif tab == "🗺️ DFD":
        _dfd_tab()
    elif tab == "📋 Collections":
        _collections_tab()
    elif tab == "🔍 Query":
        _query_tab()
    elif tab == "⚡ Triggers":
        _triggers_tab()
    elif tab == "🔌 API":
        _api_tab()
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
        "wait-time and throughput reports."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Input Entities")
        st.success("1️⃣ PATIENT — demographics, patient ID")
        st.success("2️⃣ ER_VISIT — arrival time, complaint, status")
        st.success("3️⃣ TRIAGE — ESI / CTAS / MTS score and system")
        st.success("4️⃣ ALERT — type, status, trigger time")
        st.success("5️⃣ RESOURCE — type, availability")
        st.success("6️⃣ WAIT_TIME_LOG — stage, duration")

    with col2:
        st.markdown("### Output Entities")
        st.success("1️⃣ Triage Priority Queue (ranked by urgency)")
        st.success("2️⃣ Active Alert Notifications (critical / warning)")
        st.success("3️⃣ Resource Allocation Report (used / free)")
        st.success("4️⃣ Wait-Time & Throughput Dashboard")
        st.success("5️⃣ ER Crowding Index (NEDOCS score)")

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
# ER DIAGRAM  (from entity-relationship-diagram.md)
# ─────────────────────────────────────────────
def _er_diagram_tab():
    st.markdown("### Entity Relationship Diagram")
    st.caption("Source: `entity-relationship-diagram.md`")

    # Exact mermaid from entity-relationship-diagram.md
    st.markdown("""
```mermaid
erDiagram

    ER_VISIT {
        int VisitID PK
        int LogID FK
        int AlertID FK
        int TriageID FK
        int ResourceID FK
        datetime ArrivalTime
    }

    WAIT_TIME_LOG {
        int LogID PK
        string Stage
        int Duration
    }

    ALERT {
        int AlertID PK
        string Type
        string Status
    }

    TRIAGE {
        int TriageID PK
        int Score
        string System
    }

    RESOURCE {
        int ResourceID PK
        string Type
    }

    WAIT_TIME_LOG ||--o{ ER_VISIT : Tracks
    ER_VISIT ||--o{ ALERT : Triggers
    ER_VISIT ||--|| TRIAGE : Has
    ER_VISIT }o--o{ RESOURCE : Utilizes
```
""")

    st.divider()
    st.markdown("### Relationship Summary")
    st.table({
        "From":        ["WAIT_TIME_LOG", "ER_VISIT", "ER_VISIT", "ER_VISIT"],
        "To":          ["ER_VISIT",      "ALERT",    "TRIAGE",   "RESOURCE"],
        "Cardinality": ["1 to many",     "1 to many","1 to 1",   "many to many"],
        "Label":       ["Tracks",        "Triggers", "Has",      "Utilizes"],
        "Description": [
            "One wait-time log tracks many ER visit stage records",
            "One ER visit can trigger multiple alerts",
            "Each ER visit has exactly one triage assessment",
            "An ER visit can utilize multiple resources; a resource can serve multiple visits",
        ],
    })



# ─────────────────────────────────────────────
# DFD LEVEL-2  (from backend_flow_diagram.dot)
# ─────────────────────────────────────────────
def _dfd_tab():
    st.markdown("### Data Flow Diagram — Level 2")
    st.caption("Source: `backend_flow_diagram.dot`")

    st.markdown("""
**External Entities** feed into five processes that read/write three data stores,
then deliver outputs back to ER Staff / Doctor and to downstream modules.
""")

    # ── Process descriptions ──────────────────
    st.markdown("#### Processes")
    st.table({
        "Process ID": ["2.6.1", "2.6.2", "2.6.3", "2.6.4", "2.6.5"],
        "Name": [
            "Validate ER Visit Data",
            "Calculate Triage Score (ESI/CTAS)",
            "Generate Time-Sensitive Alerts",
            "Optimize Resource Allocation",
            "Generate Throughput Reports",
        ],
        "Input": [
            "Vital Signs (M25), Patient Entry (User)",
            "Patient Profile (D1), Scoring Metrics (D2)",
            "Triage Status (D1)",
            "Wait Times (D1), Availability (D3)",
            "Visit History (D1)",
        ],
        "Output": [
            "Validated Record → D1",
            "Assigned Triage → D1",
            "Alert Trigger → M29, Transfer Notification → M27",
            "Allocation Suggestions → User",
            "Throughput Reports → User",
        ],
    })

    st.divider()

    # ── Data stores ───────────────────────────
    st.markdown("#### Data Stores")
    st.table({
        "Store ID": ["D1", "D2", "D3"],
        "Name":     ["ER_Visit_DB", "Triage_Rules_DB", "Resource_Logs"],
        "MongoDB Collection": ["er_visits + alerts + wait_time_logs", "triages", "resources"],
        "Description": [
            "Primary store: visits, alerts, wait-time stages",
            "Triage scoring rules and thresholds (ESI/CTAS/MTS)",
            "Bed, staff, equipment availability logs",
        ],
    })

    st.divider()

    # ── External entities & inter-module flows ─
    st.markdown("#### External Entities & Inter-Module Data Flows")
    st.table({
        "Entity":    ["M25: ICU Vital Signs", "M27: Cardiac ICU", "M29: Threshold Alerts", "ER Staff / Doctor"],
        "Direction": ["→ Module 26", "← Module 26", "← Module 26", "↔ Module 26"],
        "Data":      [
            "Vital Signs Data → P26.1",
            "Transfer Notification from P26.3",
            "Alert Trigger from P26.3",
            "Patient Entry → P26.1 | Allocation Suggestions ← P26.4 | Reports ← P26.5",
        ],
    })

    st.divider()

    # ── Raw DOT source ────────────────────────
    with st.expander("View raw DOT source (`backend_flow_diagram.dot`)"):
        st.code("""digraph DFD_Level2_Module26 {
    rankdir=LR;
    node [shape=rectangle, style=filled, fillcolor=lightblue];

    subgraph cluster_external {
        label = "External Entities / Modules";
        style=dashed;
        M25  [label="M25: ICU Vital Signs",  fillcolor=lightgrey];
        M27  [label="M27: Cardiac ICU",       fillcolor=lightgrey];
        M29  [label="M29: Threshold Alerts",  fillcolor=lightgrey];
        User [label="ER Staff / Doctor", shape=box, fillcolor=yellow];
    }

    node [shape=circle, fillcolor=white];
    P26_1 [label="2.6.1\\nValidate ER\\nVisit Data"];
    P26_2 [label="2.6.2\\nCalculate\\nTriage Score\\n(ESI/CTAS)"];
    P26_3 [label="2.6.3\\nGenerate\\nTime-Sensitive\\nAlerts"];
    P26_4 [label="2.6.4\\nOptimize\\nResource\\nAllocation"];
    P26_5 [label="2.6.5\\nGenerate\\nThroughput\\nReports"];

    node [shape=cylinder, fillcolor=lightyellow];
    DS_ER       [label="D1: ER_Visit_DB"];
    DS_Triage   [label="D2: Triage_Rules_DB"];
    DS_Resource [label="D3: Resource_Logs"];

    M25  -> P26_1 [label="Vital Signs Data"];
    User -> P26_1 [label="Patient Entry"];
    P26_1 -> DS_ER [label="Validated Record"];

    DS_ER     -> P26_2 [label="Patient Profile"];
    DS_Triage -> P26_2 [label="Scoring Metrics"];
    P26_2 -> DS_ER [label="Assigned Triage"];

    DS_ER -> P26_3 [label="Triage Status"];
    P26_3 -> M29  [label="Alert Trigger"];
    P26_3 -> M27  [label="Transfer Notification"];

    DS_ER       -> P26_4 [label="Wait Times"];
    DS_Resource -> P26_4 [label="Availability"];
    P26_4 -> User [label="Allocation Suggestions"];

    DS_ER -> P26_5 [label="Visit History"];
    P26_5 -> User  [label="Throughput Reports"];
}""", language="dot")


# ─────────────────────────────────────────────
# COLLECTIONS (MongoDB schemas)
# ─────────────────────────────────────────────
def _collections_tab():
    st.markdown("### MongoDB Collections  —  `module26_er`")
    st.caption("One collection per entity defined in `entity-relationship-diagram.md`.")
    st.table({
        "Collection":     ["er_visits", "wait_time_logs", "alerts", "triages", "resources"],
        "Maps to Entity": ["ER_VISIT",  "WAIT_TIME_LOG",  "ALERT",  "TRIAGE",  "RESOURCE"],
        "Primary Key":    ["VisitID",   "LogID",          "AlertID","TriageID","ResourceID"],
    })

    st.divider()
    st.markdown("#### Document Schemas")

    with st.expander("er_visits  (ER_VISIT)"):
        st.code("""{
  "VisitID":        5001,                       // int PK
  "LogID":          3001,                       // ref → wait_time_logs
  "AlertID":        4001,                       // ref → alerts (null if none)
  "TriageID":       2001,                       // ref → triages
  "ResourceID":     6001,                       // ref → resources (null if unassigned)
  "ArrivalTime":    "2026-03-18T09:42:00Z",
  "chief_complaint":"Chest pain",
  "status":         "in_treatment",             // waiting|in_triage|in_treatment|boarding|complete
  "assigned_bed":   "ER-06",
  "disposition":    null                        // discharged|admitted|transferred|left_ama
}""", language="json")

    with st.expander("wait_time_logs  (WAIT_TIME_LOG)"):
        st.code("""{
  "LogID":    3001,               // int PK
  "VisitID":  5001,               // ref → er_visits
  "Stage":    "door_to_doctor",   // door_to_doctor | door_to_disposition | los
  "Duration": 18                  // minutes (null until stage completes)
}""", language="json")

    with st.expander("alerts  (ALERT)"):
        st.code("""{
  "AlertID":     4001,                              // int PK
  "VisitID":     5001,                              // ref → er_visits
  "Type":        "ESI Level 2 — Immediate attention",
  "Status":      "active",                          // active | resolved
  "severity":    "warning",                         // critical | warning | info
  "triggered_at":"2026-03-18T09:55:00Z",
  "resolved_at": null,
  "escalated":   false
}""", language="json")

    with st.expander("triages  (TRIAGE)"):
        st.code("""{
  "TriageID":    2001,        // int PK
  "VisitID":     5001,        // ref → er_visits
  "Score":       2,           // 1–5 (1 = most urgent)
  "System":      "ESI",       // ESI | CTAS | MTS
  "pain_score":  8,
  "bp_systolic": 158,
  "bp_diastolic":96,
  "heart_rate":  112,
  "spo2":        94.0,
  "temperature": 37.8,
  "resp_rate":   22,
  "assessed_at": "2026-03-18T09:50:00Z"
}""", language="json")

    with st.expander("resources  (RESOURCE)"):
        st.code("""{
  "ResourceID":    6001,       // int PK
  "Type":          "bed",      // bed | doctor | nurse | ventilator | monitor
  "location":      "ER-Wing-A",
  "total_units":   48,
  "occupied_units":43
}""", language="json")

    st.divider()
    st.markdown("#### Live Collection Counts")
    _show_live_counts()


def _show_live_counts():
    collections = ["er_visits", "wait_time_logs", "alerts", "triages", "resources"]
    counts = {}
    try:
        for c in collections:
            counts[c] = _col(c).count_documents({})
        st.table({
            "Collection": list(counts.keys()),
            "Documents": list(counts.values()),
        })
    except Exception as e:
        st.warning(f"Could not reach MongoDB: {e}")
        st.table({
            "Collection": collections,
            "Documents": ["—"] * len(collections),
        })


# ─────────────────────────────────────────────
# QUERY  (MongoDB aggregation pipelines)
# ─────────────────────────────────────────────
def _query_tab():
    st.markdown("### MongoDB Queries  —  Module 26")

    query_options = [
        "Triage Priority Queue (Queue Management)",
        "Time Interval Calculations (Door-to-Doctor, LOS)",
        "ER Crowding Index (NEDOCS Approximation)",
        "Resource Utilisation & Prediction",
        "Throughput Report by Hour",
        "Unresolved Critical Alerts",
    ]
    sel = st.selectbox("Select a query", query_options, key="e2_query_sel")

    pipelines = {
        "Triage Priority Queue (Queue Management)": """
# Real-time triage priority queue — ordered by urgency then arrival time
db.er_visits.aggregate([
  { $match: { status: { $in: ["waiting", "in_triage", "in_treatment"] } } },
  { $lookup: {
      from: "triages", localField: "TriageID",
      foreignField: "TriageID", as: "triage" } },
  { $unwind: "$triage" },
  { $addFields: {
      wait_min: {
        $dateDiff: { startDate: "$ArrivalTime",
                     endDate: "$$NOW", unit: "minute" } } } },
  { $sort: { "triage.Score": 1, ArrivalTime: 1 } },
  { $project: { VisitID:1, chief_complaint:1, assigned_bed:1,
                status:1, wait_min:1,
                "triage.Score":1, "triage.System":1 } }
])""",
        "Time Interval Calculations (Door-to-Doctor, LOS)": """
# Door-to-doctor and LOS per visit from wait_time_logs
db.wait_time_logs.aggregate([
  { $group: {
      _id: "$VisitID",
      door_to_doctor: {
        $max: { $cond: [{ $eq: ["$Stage","door_to_doctor"] }, "$Duration", null] } },
      los: {
        $max: { $cond: [{ $eq: ["$Stage","los"] }, "$Duration", null] } }
  }},
  { $addFields: {
      door_to_doctor_status: {
        $cond: [{ $lte: ["$door_to_doctor", 30] }, "On Target", "Breached"] },
      los_status: {
        $cond: [{ $lte: ["$los", 240] }, "On Target", "Breached"] }
  }},
  { $sort: { _id: 1 } }
])""",
        "ER Crowding Index (NEDOCS Approximation)": """
# Simplified NEDOCS: occupancy ratio × 85
db.resources.aggregate([
  { $match: { Type: "bed" } },
  { $project: {
      beds_total: "$total_units",
      beds_occupied: "$occupied_units",
      nedocs_approx: {
        $round: [{ $multiply: [
          { $divide: ["$occupied_units", "$total_units"] }, 85
        ]}, 1]
      }
  }}
])""",
        "Resource Utilisation & Prediction": """
# Occupancy % with status flag per resource type
db.resources.aggregate([
  { $addFields: {
      available_units: { $subtract: ["$total_units","$occupied_units"] },
      occupancy_pct: {
        $round: [{ $multiply: [
          { $divide: ["$occupied_units","$total_units"] }, 100
        ]}, 1]
      }
  }},
  { $addFields: {
      utilisation_status: {
        $switch: { branches: [
          { case: { $gte: ["$occupancy_pct", 90] }, then: "Critical" },
          { case: { $gte: ["$occupancy_pct", 75] }, then: "High" }
        ], default: "Normal" }
      }
  }},
  { $sort: { occupancy_pct: -1 } }
])""",
        "Throughput Report by Hour": """
# Arrivals and avg LOS grouped by hour of day (today)
db.er_visits.aggregate([
  { $match: {
      ArrivalTime: {
        $gte: new Date(new Date().setHours(0,0,0,0)) } } },
  { $lookup: {
      from: "wait_time_logs", localField: "VisitID",
      foreignField: "VisitID", as: "logs" } },
  { $addFields: {
      hour: { $hour: "$ArrivalTime" },
      los: { $first: {
        $filter: { input: "$logs",
                   cond: { $eq: ["$$this.Stage","los"] } } } }
  }},
  { $group: {
      _id: "$hour",
      total_arrivals: { $sum: 1 },
      discharged: { $sum: { $cond: [{ $eq: ["$disposition","discharged"] },1,0] } },
      admitted:   { $sum: { $cond: [{ $eq: ["$disposition","admitted"]   },1,0] } },
      avg_los_min: { $avg: "$los.Duration" }
  }},
  { $sort: { _id: 1 } }
])""",
        "Unresolved Critical Alerts": """
# All unresolved critical alerts with minutes open
db.alerts.aggregate([
  { $match: { severity: "critical", Status: "active" } },
  { $lookup: {
      from: "er_visits", localField: "VisitID",
      foreignField: "VisitID", as: "visit" } },
  { $unwind: "$visit" },
  { $addFields: {
      minutes_open: {
        $dateDiff: { startDate: "$triggered_at",
                     endDate: "$$NOW", unit: "minute" } } } },
  { $sort: { triggered_at: 1 } },
  { $project: { AlertID:1, "visit.assigned_bed":1,
                Type:1, severity:1, triggered_at:1,
                minutes_open:1, escalated:1 } }
])""",
    }

    st.code(pipelines[sel], language="javascript")

    if st.button("▶️ Run Query", key="e2_exec"):
        _run_query(sel)


def _run_query(sel):
    try:
        if sel == "Triage Priority Queue (Queue Management)":
            results = list(_col("er_visits").aggregate([
                {"$match": {"status": {"$in": ["waiting", "in_triage", "in_treatment"]}}},
                {"$lookup": {"from": "triages", "localField": "TriageID",
                             "foreignField": "TriageID", "as": "triage"}},
                {"$unwind": {"path": "$triage", "preserveNullAndEmptyArrays": True}},
                {"$sort": {"triage.Score": 1, "ArrivalTime": 1}},
                {"$project": {"_id": 0, "VisitID": 1, "chief_complaint": 1,
                              "assigned_bed": 1, "status": 1,
                              "triage.Score": 1, "triage.System": 1}},
            ]))
            if results:
                st.success(f"{len(results)} document(s) returned.")
                st.json(results[:5])
            else:
                st.info("No active visits found.")

        elif sel == "Unresolved Critical Alerts":
            results = list(_col("alerts").find(
                {"severity": "critical", "Status": "active"},
                {"_id": 0, "AlertID": 1, "VisitID": 1, "Type": 1,
                 "triggered_at": 1, "escalated": 1}
            ))
            if results:
                st.success(f"{len(results)} unresolved critical alert(s).")
                st.json(results)
            else:
                st.success("No unresolved critical alerts.")

        elif sel == "Resource Utilisation & Prediction":
            results = list(_col("resources").aggregate([
                {"$addFields": {
                    "available_units": {"$subtract": ["$total_units", "$occupied_units"]},
                    "occupancy_pct": {"$round": [{"$multiply": [
                        {"$divide": ["$occupied_units", "$total_units"]}, 100]}, 1]},
                }},
                {"$sort": {"occupancy_pct": -1}},
                {"$project": {"_id": 0, "Type": 1, "total_units": 1,
                              "occupied_units": 1, "available_units": 1, "occupancy_pct": 1}},
            ]))
            if results:
                st.success(f"{len(results)} resource type(s).")
                st.json(results)
            else:
                st.info("No resource data found.")

        else:
            st.info("Live execution for this query is shown above. Results depend on your MongoDB data.")

    except Exception as e:
        st.error(f"MongoDB error: {e}")


# ─────────────────────────────────────────────
# TRIGGERS  (application-level, MongoDB has no DB triggers in free tier)
# ─────────────────────────────────────────────
def _triggers_tab():
    st.markdown("### Application-Level Trigger Logic")
    st.info(
        "MongoDB Atlas free tier does not support server-side triggers in all configurations. "
        "The logic below is implemented as Python functions called at insert/update time, "
        "mirroring the behaviour of SQL triggers."
    )

    with st.expander("🔔 on_triage_insert — Auto-create alert for Level 1 / 2 triage", expanded=True):
        st.code("""
def on_triage_insert(triage_doc: dict):
    \"\"\"Called after inserting into 'triages' collection.\"\"\"
    if triage_doc.get("Score", 5) <= 2:
        severity = "critical" if triage_doc["Score"] == 1 else "warning"
        alerts_col.insert_one({
            "VisitID":      triage_doc["VisitID"],
            "Type":         f"{triage_doc['System']} Level {triage_doc['Score']} — Immediate attention",
            "Status":       "active",
            "severity":     severity,
            "triggered_at": datetime.now(timezone.utc),
            "resolved_at":  None,
            "escalated":    False,
        })
""", language="python")

    with st.expander("⏱️ on_visit_close — Record wait-time stages on departure"):
        st.code("""
def on_visit_close(visit_id: int, arrival_time: datetime,
                   departure_time: datetime, triage_assessed_at: datetime):
    \"\"\"Called when er_visits.status is set to 'complete'.\"\"\"
    door_to_doctor = int((triage_assessed_at - arrival_time).total_seconds() / 60)
    los            = int((departure_time - arrival_time).total_seconds() / 60)

    for stage, duration in [("door_to_doctor", door_to_doctor),
                             ("door_to_disposition", los),
                             ("los", los)]:
        wait_time_logs_col.update_one(
            {"VisitID": visit_id, "Stage": stage},
            {"$set": {"Duration": duration}},
            upsert=True,
        )
""", language="python")

    with st.expander("🛏️ on_bed_change — Keep resource occupancy in sync"):
        st.code("""
def on_bed_change(old_doc: dict, new_doc: dict):
    \"\"\"Called after updating an er_visits document.\"\"\"
    # Bed assigned
    if new_doc.get("assigned_bed") and not old_doc.get("assigned_bed"):
        resources_col.update_one(
            {"Type": "bed"},
            {"$inc": {"occupied_units": 1}}
        )
    # Patient left
    if new_doc.get("status") == "complete" and old_doc.get("status") != "complete":
        if old_doc.get("assigned_bed"):
            resources_col.update_one(
                {"Type": "bed"},
                {"$inc": {"occupied_units": -1}}
            )
""", language="python")

    with st.expander("📢 escalate_stale_alerts — Escalate unresolved critical alerts after 10 min"):
        st.code("""
def escalate_stale_alerts():
    \"\"\"Run periodically (e.g. every minute via a scheduler).\"\"\"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    alerts_col.update_many(
        {
            "severity":    "critical",
            "Status":      "active",
            "escalated":   False,
            "triggered_at": {"$lte": cutoff},
        },
        {"$set": {"escalated": True}},
    )
""", language="python")


# ─────────────────────────────────────────────
# API REFERENCE
# ─────────────────────────────────────────────
def _api_tab():
    st.markdown("### REST API — Module 26")
    st.info(
        "Run the API with: `uvicorn api.main:app --reload`  \n"
        "Interactive docs: **http://localhost:8000/docs**"
    )

    endpoints = [
        # P26.1
        ("POST",   "/api/module26/visits",                    "P26.1", "Register a new ER visit (validate + persist)"),
        ("GET",    "/api/module26/visits",                    "P26.1", "List ER visits (optional ?status= filter)"),
        ("GET",    "/api/module26/visits/{visit_id}",         "P26.1", "Get a single ER visit"),
        ("PUT",    "/api/module26/visits/{visit_id}",         "P26.1", "Update visit status / bed / disposition"),
        # P26.2
        ("POST",   "/api/module26/triage",                    "P26.2", "Assign ESI/CTAS/MTS triage score"),
        ("GET",    "/api/module26/triage/queue",              "P26.2", "Priority-sorted active triage queue"),
        # P26.3
        ("GET",    "/api/module26/alerts",                    "P26.3", "List active alerts (optional ?severity=)"),
        ("PUT",    "/api/module26/alerts/{alert_id}/resolve", "P26.3", "Resolve an alert"),
        ("POST",   "/api/module26/alerts/escalate",           "P26.3", "Escalate stale critical alerts (cron)"),
        # P26.4
        ("GET",    "/api/module26/resources",                 "P26.4", "Resource utilisation + status"),
        ("PUT",    "/api/module26/resources/{resource_id}",   "P26.4", "Update occupied units"),
        ("GET",    "/api/module26/resources/crowding",        "P26.4", "NEDOCS crowding index"),
        # P26.5
        ("GET",    "/api/module26/reports/throughput",        "P26.5", "Hourly throughput report (today)"),
        ("GET",    "/api/module26/reports/wait-times/{id}",   "P26.5", "Wait-time stages for a visit"),
        # Inter-module
        ("POST",   "/api/module26/intake/m25-vitals",         "M25→26", "Receive vital signs from Module 25"),
        ("GET",    "/api/module26/export/m27-transfer",       "26→M27", "Critical alerts for Module 27 (Cardiac ICU)"),
        ("GET",    "/api/module26/export/m29-alerts",         "26→M29", "All active alerts for Module 29 (Threshold Alerts)"),
    ]

    st.table({
        "Method":      [e[0] for e in endpoints],
        "Endpoint":    [e[1] for e in endpoints],
        "DFD Process": [e[2] for e in endpoints],
        "Description": [e[3] for e in endpoints],
    })

    st.divider()
    st.markdown("#### Example: Register ER Visit")
    st.code("""
curl -X POST http://localhost:8000/api/module26/visits \\
  -H "Content-Type: application/json" \\
  -d '{
    "patient_id": 1001,
    "chief_complaint": "Chest pain with shortness of breath",
    "heart_rate": 118,
    "spo2": 91.5
  }'
""", language="bash")

    st.markdown("#### Example: Assign Triage")
    st.code("""
curl -X POST http://localhost:8000/api/module26/triage \\
  -H "Content-Type: application/json" \\
  -d '{
    "visit_id": 5001,
    "system": "ESI",
    "score": 2,
    "pain_score": 8,
    "bp_systolic": 158,
    "heart_rate": 118,
    "spo2": 91.5
  }'
""", language="bash")

    st.markdown("#### Example: Receive Vitals from M25")
    st.code("""
curl -X POST http://localhost:8000/api/module26/intake/m25-vitals \\
  -H "Content-Type: application/json" \\
  -d '{
    "patient_id": 1001,
    "heart_rate": 145,
    "spo2": 87.0,
    "bp_systolic": 185
  }'
""", language="bash")


# ─────────────────────────────────────────────
# OUTPUT  (live data + demo panel)
# ─────────────────────────────────────────────
def _output_tab():
    st.markdown("### Module Output")
    st.success("✅ Emergency Room Patient Alert System — Operational")

    # ── Live data from MongoDB ──────────────────────────────────────────────
    st.markdown("#### Live Data from MongoDB")
    col_live1, col_live2 = st.columns(2)

    with col_live1:
        st.markdown("**Recent ER Visits**")
        try:
            visits = list(_col("er_visits").find(
                {}, {"_id": 0, "VisitID": 1, "chief_complaint": 1,
                     "status": 1, "assigned_bed": 1, "ArrivalTime": 1}
            ).sort("ArrivalTime", -1).limit(5))
            if visits:
                st.json(visits)
            else:
                st.info("No visits in database yet.")
        except Exception as e:
            st.warning(f"MongoDB: {e}")

    with col_live2:
        st.markdown("**Active Alerts**")
        try:
            active_alerts = list(_col("alerts").find(
                {"Status": "active"},
                {"_id": 0, "AlertID": 1, "VisitID": 1,
                 "Type": 1, "severity": 1, "triggered_at": 1}
            ).limit(5))
            if active_alerts:
                st.json(active_alerts)
            else:
                st.success("No active alerts.")
        except Exception as e:
            st.warning(f"MongoDB: {e}")

    st.divider()

    # ── Demo insert form ────────────────────────────────────────────────────
    st.markdown("#### Register a New ER Visit (Demo)")
    with st.form("e2_new_visit"):
        f1, f2 = st.columns(2)
        patient_id    = f1.number_input("Patient ID", min_value=1, step=1)
        complaint     = f2.text_input("Chief Complaint")
        triage_system = f1.selectbox("Triage System", ["ESI", "CTAS", "MTS"])
        triage_score  = f2.slider("Triage Score (1=most urgent)", 1, 5, 3)
        submitted = st.form_submit_button("Submit Visit")

    if submitted and complaint:
        try:
            # Get next IDs
            last_visit   = _col("er_visits").find_one(sort=[("VisitID", -1)]) or {}
            last_triage  = _col("triages").find_one(sort=[("TriageID", -1)]) or {}
            last_alert   = _col("alerts").find_one(sort=[("AlertID", -1)]) or {}
            last_log     = _col("wait_time_logs").find_one(sort=[("LogID", -1)]) or {}

            visit_id   = (last_visit.get("VisitID")  or 5000) + 1
            triage_id  = (last_triage.get("TriageID") or 2000) + 1
            alert_id   = (last_alert.get("AlertID")  or 4000) + 1
            log_id     = (last_log.get("LogID")       or 3000) + 1
            now        = datetime.now(timezone.utc)

            # Insert triage
            _col("triages").insert_one({
                "TriageID": triage_id, "VisitID": visit_id,
                "Score": triage_score, "System": triage_system,
                "assessed_at": now,
            })

            # Insert visit
            _col("er_visits").insert_one({
                "VisitID": visit_id, "PatientID": patient_id,
                "TriageID": triage_id, "AlertID": None,
                "LogID": log_id, "ResourceID": None,
                "ArrivalTime": now, "chief_complaint": complaint,
                "status": "waiting", "assigned_bed": None, "disposition": None,
            })

            # Insert wait_time_log placeholder
            _col("wait_time_logs").insert_one({
                "LogID": log_id, "VisitID": visit_id,
                "Stage": "door_to_doctor", "Duration": None,
            })

            # Trigger: auto-alert for Level 1 or 2
            if triage_score <= 2:
                severity = "critical" if triage_score == 1 else "warning"
                _col("alerts").insert_one({
                    "AlertID": alert_id, "VisitID": visit_id,
                    "Type": f"{triage_system} Level {triage_score} — Immediate attention",
                    "Status": "active", "severity": severity,
                    "triggered_at": now, "resolved_at": None, "escalated": False,
                })
                _col("er_visits").update_one(
                    {"VisitID": visit_id}, {"$set": {"AlertID": alert_id}}
                )

            st.success(f"✅ Visit {visit_id} registered. Triage: {triage_system} Level {triage_score}.")
            if triage_score <= 2:
                st.warning(f"⚠️ Alert auto-generated (severity: {severity}).")
            st.rerun()

        except Exception as e:
            st.error(f"Insert failed: {e}")

    st.divider()

    # ── Static demo summary ─────────────────────────────────────────────────
    st.markdown("#### Resource Utilisation")
    st.table({
        "Resource": ["Beds", "Doctors", "Nurses", "Ventilators", "Monitors"],
        "Total": [48, 12, 24, 8, 20],
        "Occupied": [43, 10, 19, 6, 15],
        "Occupancy %": ["89.6%", "83.3%", "79.2%", "75.0%", "75.0%"],
        "Status": ["🔴 Critical", "🟠 High", "🟠 High", "🟢 Normal", "🟢 Normal"],
    })

    st.markdown("#### Throughput Report (Today by Hour — Demo)")
    st.table({
        "Hour": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"],
        "Arrivals": [8, 14, 18, 22, 16, 19, 21],
        "Discharged": [5, 10, 12, 15, 11, 14, 16],
        "Admitted": [2, 3, 4, 5, 3, 4, 4],
        "Avg LOS (min)": [185, 192, 198, 204, 188, 195, 201],
    })