import streamlit as st
import pandas as pd
import json
import os
import time
from collector import collect_metrics, get_buffer
from detector import detect_anomaly
from reasoner import analyze_with_ai

st.set_page_config(page_title="DevOps AI Agent", layout="wide")
st.title("DevOps AI Agent — Live Monitor")

INCIDENTS_FILE = "data/incidents.json"

def load_incidents():
    if not os.path.exists(INCIDENTS_FILE):
        return []
    with open(INCIDENTS_FILE, "r") as f:
        return json.load(f)

# Layout
col1, col2, col3 = st.columns(3)
cpu_metric    = col1.empty()
ram_metric    = col2.empty()
disk_metric   = col3.empty()

chart_placeholder    = st.empty()
status_placeholder   = st.empty()
incident_placeholder = st.empty()

history = {"timestamp": [], "cpu": [], "ram": [], "disk": []}

while True:
    snapshot = collect_metrics()
    buffer   = get_buffer()
    issues   = detect_anomaly(snapshot, buffer)

    # Update metric cards
    cpu_metric.metric("CPU Usage",  f"{snapshot['cpu']}%")
    ram_metric.metric("RAM Usage",  f"{snapshot['ram']}%")
    disk_metric.metric("Disk Usage", f"{snapshot['disk']}%")

    # Update rolling chart
    history["timestamp"].append(snapshot["timestamp"][-8:])
    history["cpu"].append(snapshot["cpu"])
    history["ram"].append(snapshot["ram"])
    history["disk"].append(snapshot["disk"])

    # Keep last 30 points
    for k in history:
        history[k] = history[k][-30:]

    df = pd.DataFrame(history).set_index("timestamp")
    chart_placeholder.line_chart(df)

    # Status
    if issues:
        msgs = " | ".join(i["message"] for i in issues)
        status_placeholder.error(f"ANOMALY: {msgs}")
    else:
        status_placeholder.success("System normal")

    # Recent incidents panel
    incidents = load_incidents()
    if incidents:
        incident_placeholder.subheader("Recent Incidents")
        for inc in reversed(incidents[-5:]):
            with incident_placeholder.expander(
                f"[{inc['timestamp']}] {inc.get('summary', 'Incident')}"
            ):
                analysis = inc.get("analysis", {})
                st.write(f"**Severity:** {analysis.get('severity', 'N/A').upper()}")
                st.write(f"**Root cause:** {analysis.get('root_cause', 'N/A')}")
                st.write(f"**Immediate action:** {analysis.get('immediate_action', 'N/A')}")
                if analysis.get("fixes"):
                    st.write("**Fixes:**")
                    for fix in analysis["fixes"]:
                        st.write(f"- {fix}")

    time.sleep(5)
    st.rerun()