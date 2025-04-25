#!/usr/bin/env python3
import time
import urllib.parse
import requests


LOCAL_BASE = "http://127.0.0.1:8501"

PQAI_BASE  = "https://api.projectpq.ai"

PATENTS = ["US7654321B2","US10734122B2","US10283223B2"]
INDICES = range(1,6)   

TIMEOUT = 300.0   #secs


def measure_batch(name, base_url, path_fn):

    print(f"\n=== Benchmarking {name} ===")
    total = 0.0
    calls = 0

    for pn in PATENTS:
        for idx in INDICES:
            url = base_url + path_fn(pn, idx)
            t0 = time.perf_counter()
            try:
                r = requests.get(url, timeout=TIMEOUT)
                status = r.status_code
            except Exception as e:
                status = f"ERR:{e}"
            dt = time.perf_counter() - t0

            print(f"{name:>8} {pn} [{idx}] → {dt:.3f}s (status {status})")
            total += dt
            calls += 1

    print(f"[{name} total] {calls} calls in {total:.3f}s  avg {(total/calls):.3f}s\n")
    return total, calls

# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Legacy: page-based
    legacy_path = lambda pn, i: f"/patents/{pn}/drawings/{i}"
    legacy_time, legacy_calls = measure_batch("Legacy", LOCAL_BASE, legacy_path)

    # New: OCR-based
    new_path = lambda pn, i: "/patents/{}/drawings/find?q={}".format(
        pn, urllib.parse.quote(f"figure {i}")
    )
    new_time, new_calls = measure_batch("New", LOCAL_BASE, new_path)

    # Also compare against live PQAI for fun
    pqai_time, pqai_calls = measure_batch("Official", PQAI_BASE, legacy_path)

    print("=== Summary ===")
    print(f"  Local-Legacy : {legacy_time:.3f}s for {legacy_calls} calls")
    print(f"  Local-New    : {new_time:.3f}s for {new_calls} calls")
    print(f"  Official-Leg : {pqai_time:.3f}s for {pqai_calls} calls")
    print(f"  new − leg  : {new_time-legacy_time:+.3f}s")
    print(f"  local−live : {legacy_time - pqai_time:+.3f}s")