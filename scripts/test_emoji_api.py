import urllib.request
import json
import time
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

PASS_COUNT = 0
FAIL_COUNT = 0

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    print(f"\n── {title}")

def pass_test(name, elapsed_ms):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  [PASS] {name} ({elapsed_ms:.1f}ms)")

def fail_test(name, reason, elapsed_ms):
    global FAIL_COUNT
    FAIL_COUNT += 1
    print(f"  [FAIL] {name} ({elapsed_ms:.1f}ms) -> {reason}")

def run_test(name, path, method="GET", body=None, expect_status=200, expect_fields=None, should_fail=False, expect_json=True):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            resp_body = response.read().decode("utf-8")
            elapsed = (time.perf_counter() - t0) * 1000
            
            if should_fail:
                fail_test(name, f"Expected error status but got {status}", elapsed)
                return None
                
            if status != expect_status:
                fail_test(name, f"Expected status {expect_status}, got {status}", elapsed)
                return None
                
            if not expect_json:
                pass_test(name, elapsed)
                return True
                
            res_json = json.loads(resp_body) if resp_body else {}
            
            if expect_fields:
                for k, v in expect_fields.items():
                    actual = res_json.get(k)
                    if str(actual) != str(v):
                        fail_test(name, f"Field '{k}' expected '{v}', got '{actual}'", elapsed)
                        return None
                        
            pass_test(name, elapsed)
            return res_json
            
    except urllib.error.HTTPError as e:
        elapsed = (time.perf_counter() - t0) * 1000
        if should_fail and e.code == expect_status:
            pass_test(f"{name} (Expected Error {e.code})", elapsed)
            return None
        fail_test(name, f"HTTP Error {e.code}: {e.reason}", elapsed)
        
    except Exception as e:
        elapsed = (time.perf_counter() - t0) * 1000
        if should_fail:
            pass_test(f"{name} (Expected failure: {type(e).__name__})", elapsed)
            return None
        fail_test(name, f"Error: {e}", elapsed)
    return None

def main():
    print_header("SignDecoder API Test Suite (Python Version)")
    print(f"Base URL: {BASE_URL}")
    print(f"Time:     {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ── 1. Health checks ────────────────────────────────────────────────────────
    print_section("1. Health and Availability")
    run_test("GET /health", "/health")
    run_test("GET /health/live", "/health/live", expect_fields={"alive": True})
    run_test("GET /health/ready", "/health/ready")
    run_test("GET /", "/")

    # ── 2. Standard Translation ─────────────────────────────────────────────────
    print_section("2. Standard Translation (POST /api/v1/translate)")
    run_test("Simple translation request", "/api/v1/translate", "POST", 
             {"text": "Sourav ate breakfast at home yesterday", "sign_language": "ISL", "include_details": True})
    run_test("Short translation request", "/api/v1/translate", "POST", 
             {"text": "I go school", "sign_language": "ISL", "include_details": False})
    run_test("Question translation request", "/api/v1/translate", "POST", 
             {"text": "Where is the hospital?", "sign_language": "ISL", "include_details": True})

    # ── 3. Emoji ML Endpoint — Happy Path ──────────────────────────────────────
    print_section("3. Emoji ML (POST /api/convert-to-emoji) — Valid inputs")
    happy_cases = [
        ("I eat breakfast morning", "meal gloss"),
        ("she drink coffee daily", "daily routine"),
        ("boy run school fast", "action gloss"),
        ("family celebrate birthday", "event gloss"),
        ("he read book night", "leisure gloss"),
        ("rain fall heavy outside", "weather gloss"),
        ("doctor help sick person", "medical gloss"),
        ("yesterday home sourav breakfast eat", "full ISL sentence")
    ]
    for gloss, label in happy_cases:
        run_test(f"Convert: {label}", "/api/convert-to-emoji", "POST", 
                 {"text": gloss}, expect_fields={"success": True})

    # ── 4. Emoji ML Endpoint — Error Scenarios ─────────────────────────────────
    print_section("4. Emoji ML — Error / Edge Cases")
    run_test("Empty string body", "/api/convert-to-emoji", "POST", {"text": ""}, expect_status=422, should_fail=True)
    run_test("Whitespace only", "/api/convert-to-emoji", "POST", {"text": "   "}, expect_status=422, should_fail=True)
    run_test("Missing text field", "/api/convert-to-emoji", "POST", {"wrong_key": "hello"}, expect_status=422, should_fail=True)
    run_test("Very long input", "/api/convert-to-emoji", "POST", {"text": "word " * 100})
    run_test("Single word input", "/api/convert-to-emoji", "POST", {"text": "eat"})
    run_test("Numbers in gloss", "/api/convert-to-emoji", "POST", {"text": "3 people eat food"})
    run_test("Mixed case input", "/api/convert-to-emoji", "POST", {"text": "YESTERDAY HOME EAT FOOD"})

    # ── 5. Performance / Load Tests ─────────────────────────────────────────────
    print_section("5. Performance — Consecutive Requests")
    times = []
    for i in range(1, 6):
        t0 = time.perf_counter()
        res = run_test(f"Consecutive Request #{i}", "/api/convert-to-emoji", "POST", {"text": "I eat breakfast morning"})
        elapsed = (time.perf_counter() - t0) * 1000
        if res:
            times.append(elapsed)
            print(f"     → Result Emoji: {res.get('emoji')}")
            
    if times:
        print(f"  ℹ Avg: {sum(times)/len(times):.1f}ms  |  Min: {min(times):.1f}ms  |  Max: {max(times):.1f}ms")

    # ── 6. Batch conversion (display table) ─────────────────────────────────────
    print_section("6. Batch Gloss Conversion Table")
    batch = [
        "I eat breakfast",
        "she drink coffee morning",
        "boy runs to school",
        "we celebrate birthday",
        "he is angry and fights",
        "family eats dinner together"
    ]
    print(f"  {'GLOSS INPUT':<35} | {'EMOJI OUTPUT'}")
    print("  " + "-" * 60)
    for g in batch:
        res = run_test(g, "/api/convert-to-emoji", "POST", {"text": g})
        if res:
            # We overwrite print above inside run_test so let's format nice output
            print(f"  → {g:<33} | {res.get('emoji')}")

    # ── 7. Documentation Endpoints ──────────────────────────────────────────────
    print_section("7. Documentation Endpoints")
    run_test("GET /docs", "/docs", expect_json=False)
    run_test("GET /redoc", "/redoc", expect_json=False)

    # ── SUMMARY ─────────────────────────────────────────────────────────────────
    total = PASS_COUNT + FAIL_COUNT
    print_header("TEST SUMMARY")
    print(f"  Total Tests Run: {total}")
    print(f"  Passed:          {PASS_COUNT}")
    print(f"  Failed:          {FAIL_COUNT}")
    if FAIL_COUNT == 0:
        print("  ✦ All tests passed! API is healthy.")
    else:
        print(f"  ✗ {FAIL_COUNT} test(s) failed. Please check backend logs.")
    print("=" * 70)

if __name__ == "__main__":
    main()
