import time
from collector import collect_metrics, get_buffer
from detector import detect_anomaly
from reasoner import analyze_with_ai   # changed

POLL_INTERVAL = 5
COOLDOWN = 30

last_alert_time = 0

print("DevOps AI Agent started. Press Ctrl+C to stop.\n")

while True:
    try:
        snapshot = collect_metrics()
        buffer   = get_buffer()
        issues   = detect_anomaly(snapshot, buffer)

        status = f"[{snapshot['timestamp']}] CPU:{snapshot['cpu']}% RAM:{snapshot['ram']}% Disk:{snapshot['disk']}%"

        if issues:
            now = time.time()
            if now - last_alert_time > COOLDOWN:
                print(f"\n{'='*60}")
                print("ANOMALY DETECTED")
                print(status)
                for issue in issues:
                    print(f"  -> {issue['message']}")

                print("\nAsking Gemini for analysis...")
                analysis = analyze_with_ai(snapshot, issues, buffer)  # changed

                if analysis:
                    print(f"\nSeverity : {analysis['severity'].upper()}")
                    print(f"Summary  : {analysis['summary']}")
                    print(f"Cause    : {analysis['root_cause']}")
                    print(f"Action   : {analysis['immediate_action']}")
                    print("Fixes:")
                    for fix in analysis.get("fixes", []):
                        print(f"  - {fix}")

                print(f"{'='*60}\n")
                last_alert_time = now
        else:
            print(status + " — normal")

        time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\nAgent stopped.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(POLL_INTERVAL)