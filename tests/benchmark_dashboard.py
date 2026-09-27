import time
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models import User, Meter, Reading, Alert
from backend.app.auth import create_access_token

def percentile(values, p):
    sorted_values = sorted(values)
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    d = k - f
    return sorted_values[f] + d * (sorted_values[c] - sorted_values[f])

def run_benchmark():
    client = TestClient(app)
    db = SessionLocal()

    # Find an operator or administrative user for full authorized scope
    user = db.query(User).filter(User.role.in_(["OPERATOR", "ADMIN"])).first()
    if not user:
        user = db.query(User).first()

    token = create_access_token({
        "sub": user.id,
        "email": user.email,
        "user_metadata": {"role": user.role, "org_id": user.organization_id}
    })
    headers = {"Authorization": f"Bearer {token}"}

    dataset_size = {
        "meters_count": db.query(Meter).count(),
        "readings_count": db.query(Reading).count(),
        "alerts_count": db.query(Alert).count(),
        "users_count": db.query(User).count(),
    }
    db.close()

    endpoints = [
        "/api/dashboard/summary",
        "/api/meters",
        "/api/alerts"
    ]

    # Warm-up pass
    for ep in endpoints:
        for _ in range(5):
            client.get(ep, headers=headers)

    sample_count = 100
    results = {}

    for ep in endpoints:
        latencies = []
        for _ in range(sample_count):
            t0 = time.perf_counter()
            res = client.get(ep, headers=headers)
            t1 = time.perf_counter()
            assert res.status_code == 200, f"Endpoint {ep} failed with {res.status_code}"
            latencies.append((t1 - t0) * 1000.0)  # ms

        results[ep] = {
            "sample_count": len(latencies),
            "min_ms": round(min(latencies), 2),
            "p50_ms": round(percentile(latencies, 50), 2),
            "p95_ms": round(percentile(latencies, 95), 2),
            "max_ms": round(max(latencies), 2),
        }

    return dataset_size, results

if __name__ == "__main__":
    dataset, results = run_benchmark()
    print("DATASET_SIZE:", dataset)
    for ep, stats in results.items():
        print(f"ENDPOINT: {ep} -> samples={stats['sample_count']}, min={stats['min_ms']}ms, p50={stats['p50_ms']}ms, p95={stats['p95_ms']}ms, max={stats['max_ms']}ms")
