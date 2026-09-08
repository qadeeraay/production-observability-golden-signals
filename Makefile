.PHONY: test validate-rules validate-dashboards simulate-alert traffic clean help

help:
	@echo "Available commands:"
	@echo "  make test                - Validate Prometheus rules and Grafana dashboards"
	@echo "  make validate-rules      - Validate PromQL recording and alerting rules"
	@echo "  make validate-dashboards - Validate Grafana dashboard JSON schemas"
	@echo "  make simulate-alert      - Simulate end-to-end incident & Alertmanager routing"
	@echo "  make traffic             - Run synthetic traffic generator (normal)"
	@echo "  make traffic-chaos       - Run synthetic traffic with 500 error chaos"
	@echo "  make clean               - Remove temporary cache files"

test: validate-rules validate-dashboards simulate-alert

validate-rules:
	python3 tests/validate_prometheus_rules.py

validate-dashboards:
	python3 tests/validate_grafana_dashboards.py

simulate-alert:
	python3 tests/simulate_incident_alerting.py

traffic:
	python3 traffic-simulator/traffic_generator.py --duration 10 --chaos none

traffic-chaos:
	python3 traffic-simulator/traffic_generator.py --duration 10 --chaos errors

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
