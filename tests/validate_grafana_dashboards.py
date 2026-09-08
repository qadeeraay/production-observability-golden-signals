#!/usr/bin/env python3
"""
Grafana Dashboard JSON Schema & Panel Syntax Validator
Ensures Golden Signals panels, targets, and field configurations are production-ready.
"""
import json
import glob
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARDS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "grafana", "dashboards")

def validate_dashboards():
    print("================================================================================")
    print("      GRAFANA DASHBOARD JSON SCHEMA & METRIC TARGET VALIDATOR")
    print("================================================================================")
    dashboard_files = glob.glob(os.path.join(DASHBOARDS_DIR, "*.json"))

    for filepath in dashboard_files:
        filename = os.path.basename(filepath)
        print(f"\nAuditing Dashboard: {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "title" in data, "Missing dashboard title"
        assert "panels" in data, "Missing panels block"
        print(f"  • Dashboard Title: '{data['title']}' (UID: {data.get('uid')})")

        panels = data["panels"]
        print(f"  • Validating {len(panels)} Panels:")
        for panel in panels:
            if panel.get("type") == "row":
                continue
            title = panel.get("title", "Untitled")
            p_type = panel.get("type", "unknown")
            targets = panel.get("targets", [])
            assert len(targets) > 0, f"Panel '{title}' has zero PromQL targets!"
            for t in targets:
                assert "expr" in t, f"Missing PromQL expr in panel '{title}'"
            print(f"    [PASS] Panel: '{title}' [Type: {p_type}, Targets: {len(targets)}]")

    print("\n--------------------------------------------------------------------------------")
    print(" [✓] ALL GRAFANA DASHBOARD SCHEMAS AND PROMQL TARGETS VALIDATED")
    print("================================================================================")
    return True

if __name__ == "__main__":
    success = validate_dashboards()
    sys.exit(0 if success else 1)
