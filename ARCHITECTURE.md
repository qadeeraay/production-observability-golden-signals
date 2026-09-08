# Architectural Specification: Site Reliability Engineering & Observability

## 1. The 4 Golden Signals Framework (Google SRE Standard)

This platform structures telemetry across four critical dimensions:

1. **Latency:** The time it takes to service a request.
   - We record percentiles via `histogram_quantile(0.99, ...)` rather than mathematical averages (`avg`), because averages disguise severe tail latencies experienced by the most active users.
2. **Traffic:** A measure of demand placed on the system.
   - Tracked via request rates (`sum(rate(http_requests_total[5m]))`) to differentiate between latency caused by organic demand vs application deadlocks.
3. **Errors:** The rate of requests that fail explicitly or implicitly.
   - Differentiated into 4xx (client errors) and 5xx (server faults). Only 5xx errors consume the service's error budget.
4. **Saturation:** How "full" the service or underlying node is.
   - Tracks memory cgroup utilization (`process_resident_memory_bytes` against hard container memory ceilings) to alert ahead of kernel `OOMKilled` terminations.

---

## 2. Multi-Window Multi-Burn-Rate Alerting Architecture

Traditional threshold alerting (e.g. *"alert if error rate > 1%"*) creates two fatal flaws:
- **Small window (e.g., 2 min):** High false positives on small, momentary traffic dips.
- **Large window (e.g., 1 hour):** Delays incident detection by up to an hour for severe outages.

To resolve this, the architecture adopts the **Google SRE Multi-Burn-Rate** formula:
$$\text{Burn Rate} = \frac{\text{Observed Error Rate}}{1 - \text{SLO Target}}$$
For a 99.9% availability target:
- $1 - \text{SLO} = 0.001$ (0.1% allowable error budget).
- A **$14.4\times$ burn rate** exhausts 2% of the monthly error budget in 1 hour ($0.1\% \times 14.4 = 1.44\%$ error rate).
- Alertmanager triggers a critical page immediately if this burn rate is sustained over a 2-minute lookback window, ensuring rapid MTTD while eliminating false alarms.
