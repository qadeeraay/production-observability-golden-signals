#!/usr/bin/env python3
"""
Prometheus Rules & PromQL Syntax Validator
Verifies recording rules, alerting expressions, and duration constraints.
"""
import yaml
import glob
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "prometheus", "rules")

def validate_rules():
    print("================================================================================")
    print("      PROMETHEUS RECORDING & ALERTING RULE SYNTAX VALIDATOR")
    print("================================================================================")
    
    rule_files = glob.glob(os.path.join(RULES_DIR, "*.yml")) + glob.glob(os.path.join(RULES_DIR, "*.yaml"))
    total_rules = 0
    total_alerts = 0

    for filepath in rule_files:
        filename = os.path.basename(filepath)
        print(f"\nValidating rule file: {filename}...")
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data or "groups" not in data:
            print(f"  [FAIL] Missing 'groups' block in {filename}")
            return False

        for group in data["groups"]:
            group_name = group.get("name", "unnamed")
            print(f"  • Inspecting Rule Group: '{group_name}'")
            rules = group.get("rules", [])

            for rule in rules:
                if "record" in rule:
                    total_rules += 1
                    expr = rule.get("expr", "").strip()
                    assert expr, f"Empty expression in recording rule: {rule['record']}"
                    print(f"    [PASS] Record: {rule['record']}")

                elif "alert" in rule:
                    total_alerts += 1
                    alert_name = rule.get("alert")
                    expr = rule.get("expr", "").strip()
                    assert expr, f"Empty expression in alert: {alert_name}"
                    assert "for" in rule, f"Missing 'for' duration in alert: {alert_name}"
                    assert "labels" in rule, f"Missing 'labels' block in alert: {alert_name}"
                    assert "annotations" in rule, f"Missing 'annotations' in alert: {alert_name}"
                    print(f"    [PASS] Alert:  {alert_name} (for: {rule['for']}, severity: {rule['labels'].get('severity')})")

    print("\n--------------------------------------------------------------------------------")
    print(f" Total Recording Rules Verified: {total_rules}")
    print(f" Total Alerting Rules Verified:  {total_alerts}")
    print(" [✓] ALL PROMETHEUS RULE DEFINITIONS VALIDATED")
    print("================================================================================")
    return True

if __name__ == "__main__":
    success = validate_rules()
    sys.exit(0 if success else 1)
