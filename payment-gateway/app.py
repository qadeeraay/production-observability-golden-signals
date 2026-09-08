#!/usr/bin/env python3
"""
Production Mock Payment Gateway Service
Simulates payment API traffic, latencies, and 5xx errors, exporting standard Prometheus metrics.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import random
import urllib.parse

# In-memory Prometheus metric state
metrics_lock = threading.Lock()
req_200 = 2500
req_500 = 5

latency_buckets = {
    0.05: 2100,
    0.10: 2420,
    0.20: 2485,
    0.30: 2498,
    0.50: 2503,
}
latency_inf = 2505
latency_sum = 65.4
latency_count = 2505

chaos_mode = "none" # "none", "errors", "latency"

def background_traffic_worker():
    """Generates a steady realistic background traffic stream."""
    global req_200, req_500, latency_inf, latency_sum, latency_count, chaos_mode
    while True:
        time.sleep(1.0)
        with metrics_lock:
            # Steady 8-15 requests per second
            batch_size = random.randint(8, 15)
            for _ in range(batch_size):
                latency_count += 1
                if chaos_mode == "errors" or random.random() < 0.001:
                    is_err = (chaos_mode == "errors" and random.random() < 0.35) or (random.random() < 0.001)
                else:
                    is_err = False

                if is_err:
                    req_500 += 1
                    lat = random.uniform(0.04, 0.08)
                elif chaos_mode == "latency":
                    req_200 += 1
                    lat = random.uniform(0.35, 0.55) # P99 breach (>300ms)
                else:
                    req_200 += 1
                    lat = random.uniform(0.012, 0.035)

                latency_sum += lat
                latency_inf += 1
                for b in sorted(latency_buckets.keys()):
                    if lat <= b:
                        latency_buckets[b] += 1

class MetricHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default access logging to keep stdout clean
        pass

    def do_GET(self):
        global req_200, req_500, latency_inf, latency_sum, latency_count, chaos_mode
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/metrics":
            with metrics_lock:
                lines = [
                    "# HELP http_requests_total Total number of HTTP requests.",
                    "# TYPE http_requests_total counter",
                    f'http_requests_total{{status="200",service="payment-gateway",environment="production"}} {req_200}',
                    f'http_requests_total{{status="500",service="payment-gateway",environment="production"}} {req_500}',
                    "# HELP http_request_duration_seconds HTTP request latency in seconds.",
                    "# TYPE http_request_duration_seconds histogram",
                ]
                for b, count in sorted(latency_buckets.items()):
                    lines.append(f'http_request_duration_seconds_bucket{{le="{b}",service="payment-gateway",environment="production"}} {count}')
                lines.append(f'http_request_duration_seconds_bucket{{le="+Inf",service="payment-gateway",environment="production"}} {latency_inf}')
                lines.append(f'http_request_duration_seconds_sum{{service="payment-gateway",environment="production"}} {latency_sum:.4f}')
                lines.append(f'http_request_duration_seconds_count{{service="payment-gateway",environment="production"}} {latency_count}')
                lines.append("")
                body = "\n".join(lines).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/chaos/errors":
            with metrics_lock:
                chaos_mode = "errors"
            body = b'{"status":"chaos_enabled","mode":"errors"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/chaos/latency":
            with metrics_lock:
                chaos_mode = "latency"
            body = b'{"status":"chaos_enabled","mode":"latency"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path == "/chaos/reset":
            with metrics_lock:
                chaos_mode = "none"
            body = b'{"status":"chaos_reset","mode":"none"}\n'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        # Regular application route (e.g. /checkout or /)
        query = urllib.parse.parse_qs(parsed.query)
        is_chaos = "chaos" in query and query["chaos"][0] == "errors"

        with metrics_lock:
            latency_count += 1
            latency_inf += 1
            if is_chaos or (chaos_mode == "errors" and random.random() < 0.40):
                req_500 += 1
                lat = 0.05
                status_code = 500
                resp = b'{"status":"error","message":"Database thread pool exhausted"}\n'
            else:
                req_200 += 1
                lat = random.uniform(0.015, 0.035)
                status_code = 200
                resp = b'{"status":"ok","message":"Payment processed successfully"}\n'

            latency_sum += lat
            for b in sorted(latency_buckets.keys()):
                if lat <= b:
                    latency_buckets[b] += 1

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

def run():
    worker = threading.Thread(target=background_traffic_worker, daemon=True)
    worker.start()
    server = HTTPServer(("0.0.0.0", 8080), MetricHandler)
    print("Payment Gateway mock service listening on port 8080 (metrics at /metrics)...")
    server.serve_forever()

if __name__ == "__main__":
    run()
