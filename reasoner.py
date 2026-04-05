import google.genai as genai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model = "gemini-2.0-flash"

INCIDENTS_FILE = "data/incidents.json"

def load_incidents():
    if not os.path.exists(INCIDENTS_FILE):
        return []
    with open(INCIDENTS_FILE, "r") as f:
        return json.load(f)

def save_incident(incident):
    incidents = load_incidents()
    incidents.append(incident)
    incidents = incidents[-100:]
    with open(INCIDENTS_FILE, "w") as f:
        json.dump(incidents, f, indent=2)

def get_similar_past_incidents(current_issues, n=3):
    all_incidents = load_incidents()
    if not all_incidents:
        return []
    current_types = {i.get("metric", i.get("type", "")) for i in current_issues}
    similar = [
        inc for inc in all_incidents
        if any(
            issue.get("metric", issue.get("type", "")) in current_types
            for issue in inc.get("issues", [])
        )
    ]
    return similar[-n:]

def analyze_with_gemini(snapshot, issues, buffer):
    if not issues:
        return None

    past = get_similar_past_incidents(issues)
    past_context = ""
    if past:
        past_context = "\n\nSimilar past incidents for context:\n"
        for p in past:
            past_context += f"- [{p['timestamp']}] {[i['message'] for i in p['issues']]} → AI said: {p.get('summary', 'N/A')}\n"

    top_procs = snapshot.get("top_processes", [])
    proc_summary = ", ".join(
        f"{p['name']} (CPU:{p['cpu']}% RAM:{p['ram']:.1f}%)"
        for p in top_procs[:3]
    )

    prompt = f"""You are an expert DevOps AI assistant analyzing a system anomaly.

Current system state:
- CPU: {snapshot['cpu']}%
- RAM: {snapshot['ram']}%
- Disk: {snapshot['disk']}%
- Top processes: {proc_summary}

Detected issues:
{json.dumps(issues, indent=2)}
{past_context}

Respond with a JSON object only (no markdown, no extra text, no backticks) with these exact keys:
{{
  "summary": "one-sentence summary of what is happening",
  "root_cause": "most likely root cause in 1-2 sentences",
  "severity": "low | medium | high | critical",
  "fixes": ["fix suggestion 1", "fix suggestion 2", "fix suggestion 3"],
  "immediate_action": "single most important thing to do right now"
}}"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        raw = response.text.strip()

        # Strip markdown code fences if Gemini adds them anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        analysis = json.loads(raw)

    except json.JSONDecodeError:
        analysis = {
            "summary": "Anomaly detected — could not parse AI response",
            "root_cause": "Review system manually",
            "severity": "medium",
            "fixes": [],
            "immediate_action": "Check top processes manually"
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

    incident = {
        "timestamp": snapshot["timestamp"],
        "metrics": {k: snapshot[k] for k in ["cpu", "ram", "disk"]},
        "issues": issues,
        "summary": analysis.get("summary", ""),
        "analysis": analysis
    }
    save_incident(incident)

    return analysis