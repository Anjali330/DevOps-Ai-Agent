import numpy as np
from sklearn.ensemble import IsolationForest

# Fallback thresholds (used before ML model has enough data)
THRESHOLDS = {
    "cpu": 85,
    "ram": 80,
    "disk": 90
}

# Isolation Forest instance (retrained on each check)
_model = None
_trained_on = 0  # how many samples it was trained on

def _extract_features(snapshot):
    return [snapshot["cpu"], snapshot["ram"], snapshot["disk"]]

def train_model(buffer):
    global _model, _trained_on
    if len(buffer) < 20:
        return False  # not enough data yet
    X = np.array([_extract_features(s) for s in buffer])
    _model = IsolationForest(contamination=0.1, random_state=42)
    _model.fit(X)
    _trained_on = len(buffer)
    return True

def detect_anomaly(snapshot, buffer):
    issues = []

    # Try ML detection first
    if train_model(buffer) and _model is not None:
        features = np.array([_extract_features(snapshot)])
        score = _model.decision_function(features)[0]
        prediction = _model.predict(features)[0]  # -1 = anomaly, 1 = normal

        if prediction == -1:
            issues.append({
                "type": "ml_anomaly",
                "score": round(score, 4),
                "message": f"ML anomaly detected (score: {score:.3f})",
                "metrics": {
                    "cpu": snapshot["cpu"],
                    "ram": snapshot["ram"],
                    "disk": snapshot["disk"]
                }
            })
    else:
        # Fallback: threshold-based
        if snapshot["cpu"] > THRESHOLDS["cpu"]:
            issues.append({
                "type": "threshold",
                "metric": "cpu",
                "value": snapshot["cpu"],
                "threshold": THRESHOLDS["cpu"],
                "message": f"High CPU: {snapshot['cpu']}% (threshold: {THRESHOLDS['cpu']}%)"
            })
        if snapshot["ram"] > THRESHOLDS["ram"]:
            issues.append({
                "type": "threshold",
                "metric": "ram",
                "value": snapshot["ram"],
                "threshold": THRESHOLDS["ram"],
                "message": f"High RAM: {snapshot['ram']}% (threshold: {THRESHOLDS['ram']}%)"
            })
        if snapshot["disk"] > THRESHOLDS["disk"]:
            issues.append({
                "type": "threshold",
                "metric": "disk",
                "value": snapshot["disk"],
                "threshold": THRESHOLDS["disk"],
                "message": f"High disk: {snapshot['disk']}% (threshold: {THRESHOLDS['disk']}%)"
            })

    return issues