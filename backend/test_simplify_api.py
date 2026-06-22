import urllib.request
import json
import sys 

def test_translate():
    url = "http://127.0.0.1:8000/api/v1/translate"
    data = {
        "text": "the physician treated the patient.",
        "sign_language": "ISL",
        "simplify": True,
        "include_details": True
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        print("Sending request to FastAPI with simplify=True (may take time on first run)...", flush=True)
        with urllib.request.urlopen(req, timeout=180) as res:
            response = json.loads(res.read().decode("utf-8"))
            print("STATUS: SUCCESS", flush=True)
            # Use ensure_ascii=True to avoid console printing crashes
            print(json.dumps(response, indent=2, ensure_ascii=True), flush=True)
    except Exception as e:
        print(f"STATUS: FAILED - {e}", flush=True)

if __name__ == "__main__":
    test_translate()
