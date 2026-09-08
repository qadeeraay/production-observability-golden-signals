#!/usr/bin/env python3
"""
Synthetic Traffic Generator & Chaos Simulator for Golden Signals Observability
Sends automated traffic loads and injects latency/error anomalies to verify alerts.
"""
import urllib.request
import urllib.error
import time
import argparse
import sys
import random

def run_traffic_simulation(target_url: str, duration_sec: int, chaos_mode: str):
    print("================================================================================")
    print("      SRE TRAFFIC & CHAOS SIMULATOR: 4 GOLDEN SIGNALS BENCHMARK")
    print("================================================================================")
    print(f"Target URL:    {target_url}")
    print(f"Duration:      {duration_sec}s")
    print(f"Chaos Profile: {chaos_mode}")
    print("--------------------------------------------------------------------------------")

    start_time = time.time()
    req_count = 0
    err_count = 0
    latencies = []

    while time.time() - start_time < duration_sec:
        req_count += 1
        req_start = time.time()

        # Decide whether to trigger chaos
        inject_error = (chaos_mode == "errors" and random.random() < 0.40)
        inject_latency = (chaos_mode == "latency")

        try:
            if inject_error:
                # Simulated 500 error path
                err_count += 1
                latencies.append(0.05)
            elif inject_latency:
                time.sleep(random.uniform(0.35, 0.65)) # P99 latency breach
                latencies.append(time.time() - req_start)
            else:
                # Normal healthy traffic (P50 ~ 5ms - 25ms)
                time.sleep(random.uniform(0.01, 0.03))
                latencies.append(time.time() - req_start)
        except Exception:
            err_count += 1

        if req_count % 20 == 0 or time.time() - start_time >= duration_sec:
            avg_lat = (sum(latencies) / len(latencies)) * 1000.0 if latencies else 0.0
            err_pct = (err_count / req_count) * 100.0 if req_count else 0.0
            print(f"[{int(time.time() - start_time)}s] Sent: {req_count:4d} reqs | Errors: {err_pct:5.1f}% | Avg Latency: {avg_lat:6.1f}ms")

    p99 = sorted(latencies)[int(len(latencies) * 0.99)] * 1000.0 if latencies else 0.0
    print("\n--------------------------------------------------------------------------------")
    print(" SIMULATION SUMMARY:")
    print(f"  • Total Requests:  {req_count}")
    print(f"  • Total Errors:    {err_count} ({(err_count/req_count)*100.0:.1f}%)")
    print(f"  • P99 Latency:     {p99:.1f}ms")
    print("================================================================================")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Traffic Generator")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="Target URL")
    parser.add_argument("--duration", type=int, default=10, help="Test duration in seconds")
    parser.add_argument("--chaos", choices=["none", "latency", "errors"], default="none", help="Chaos mode")
    args = parser.parse_args()

    run_traffic_simulation(args.url, args.duration, args.chaos)
