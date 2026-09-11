#!/usr/bin/env python3
"""
Unit test suite for SRE Observability stack configurations (Alertmanager, Prometheus, Loki).
"""
import unittest
import os
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)


class TestObservabilityConfigurations(unittest.TestCase):

    def test_alertmanager_route_and_inhibit_rules(self):
        """Verify Alertmanager routing tiers and severity inhibition rules."""
        am_file = os.path.join(PROJECT_DIR, "alertmanager", "alertmanager.yml")
        self.assertTrue(os.path.isfile(am_file))
        with open(am_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("route", data)
        self.assertEqual(data["route"]["receiver"], "sre-oncall-team")
        
        # Verify inhibit rules exist for critical -> warning suppression
        inhibit_rules = data.get("inhibit_rules", [])
        self.assertGreaterEqual(len(inhibit_rules), 1)
        self.assertEqual(inhibit_rules[0]["source_match"]["severity"], "critical")
        self.assertEqual(inhibit_rules[0]["target_match"]["severity"], "warning")

    def test_prometheus_scrape_configs(self):
        """Verify Prometheus scrape targets and rule file references."""
        prom_file = os.path.join(PROJECT_DIR, "prometheus", "prometheus.yml")
        self.assertTrue(os.path.isfile(prom_file))
        with open(prom_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIn("scrape_configs", data)
        job_names = [j["job_name"] for j in data["scrape_configs"]]
        self.assertIn("payment-gateway", job_names)
        self.assertIn("prometheus", job_names)

    def test_loki_and_promtail_configs(self):
        """Verify Loki server config and Promtail client target."""
        loki_file = os.path.join(PROJECT_DIR, "loki", "loki-config.yaml")
        promtail_file = os.path.join(PROJECT_DIR, "promtail", "promtail-config.yaml")

        self.assertTrue(os.path.isfile(loki_file))
        self.assertTrue(os.path.isfile(promtail_file))

        with open(loki_file, "r", encoding="utf-8") as f:
            loki_docs = list(yaml.safe_load_all(f))
        self.assertGreaterEqual(len(loki_docs), 1)
        self.assertIn("server", loki_docs[0])
        self.assertIn("schema_config", loki_docs[0])

        with open(promtail_file, "r", encoding="utf-8") as f:
            promtail_data = yaml.safe_load(f)
        self.assertIn("clients", promtail_data)
        self.assertIn("scrape_configs", promtail_data)


if __name__ == "__main__":
    unittest.main()
