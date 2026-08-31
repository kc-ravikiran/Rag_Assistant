"""
Sample Data Generator
Creates realistic logistics test data for all four document types.
Run this once to populate the data/ directories before ingesting.
"""

import csv
import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


CARRIERS = ["BlueDart", "Delhivery", "FedEx", "DHL", "Ecom Express", "XpressBees"]
STATUSES = ["Delivered", "In Transit", "Out for Delivery", "Delayed", "Failed Attempt", "Returned"]
SLA_STATUSES = ["Met", "Breached", "At Risk"]
ZONES = ["North", "South", "East", "West", "Central"]
DRIVERS = [
    ("D001", "Ravi Kumar"), ("D002", "Suresh Patel"), ("D003", "Anand Verma"),
    ("D004", "Priya Sharma"), ("D005", "Deepak Singh"), ("D006", "Kavita Reddy"),
]
CITIES = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Kolkata"]


def random_date(start_days_ago=30, end_days_ago=0):
    base = datetime.now() - timedelta(days=random.randint(end_days_ago, start_days_ago))
    return base.strftime("%Y-%m-%d %H:%M")


def generate_shipments(out_dir: Path, n=200):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, n + 1):
        driver_id, driver_name = random.choice(DRIVERS)
        status = random.choice(STATUSES)
        scheduled = random_date(10, 1)
        delay = 0 if status == "Delivered" else random.randint(0, 300)
        sla_status = "Met" if delay == 0 else ("Breached" if delay > 60 else "At Risk")
        rows.append({
            "shipment_id": f"SHP{i:05d}",
            "order_id": f"ORD{random.randint(100000, 999999)}",
            "customer_name": f"Customer {i}",
            "origin": random.choice(CITIES),
            "destination": random.choice(CITIES),
            "carrier": random.choice(CARRIERS),
            "driver_id": driver_id,
            "driver_name": driver_name,
            "status": status,
            "zone": random.choice(ZONES),
            "route_code": f"RT-{random.choice(ZONES[:3])}-{random.randint(1, 20):02d}",
            "scheduled_delivery": scheduled,
            "actual_delivery": random_date(1, 0) if status == "Delivered" else "",
            "delay_minutes": delay,
            "sla_deadline": scheduled,
            "sla_status": sla_status,
            "weight_kg": round(random.uniform(0.5, 50), 2),
            "remarks": "Attempted delivery - customer absent" if status == "Failed Attempt" else "",
        })

    with open(out_dir / "shipments.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ Generated {n} shipment records → {out_dir}/shipments.csv")


def generate_routes(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for zone in ZONES:
        for i in range(1, 11):
            rows.append({
                "route_code": f"RT-{zone[:3].upper()}-{i:02d}",
                "zone": zone,
                "hub": f"{zone} Hub",
                "coverage_area": f"{zone} Sector {i}",
                "avg_distance_km": random.randint(10, 80),
                "avg_stops": random.randint(15, 40),
                "assigned_driver": random.choice(DRIVERS)[1],
                "sla_hours": random.choice([24, 48, 72]),
                "active": "Yes",
            })

    with open(out_dir / "routes.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Zone JSON
    zone_data = {z: {"hub": f"{z} Hub", "sla_hours": random.choice([24, 48]), "routes": random.randint(8, 15)} for z in ZONES}
    with open(out_dir / "zones.json", "w") as f:
        json.dump(zone_data, f, indent=2)
    print(f"  ✅ Generated route & zone data → {out_dir}/")


def generate_logs(out_dir: Path, n=300):
    out_dir.mkdir(parents=True, exist_ok=True)
    events = ["Picked Up", "In Transit", "Out for Delivery", "Delivered", "Delivery Failed", "Returned to Hub"]
    rows = []
    for i in range(1, n + 1):
        driver_id, driver_name = random.choice(DRIVERS)
        rows.append({
            "log_id": f"LOG{i:06d}",
            "timestamp": random_date(2, 0),
            "shipment_id": f"SHP{random.randint(1, 200):05d}",
            "event": random.choice(events),
            "driver_id": driver_id,
            "driver_name": driver_name,
            "location": random.choice(CITIES),
            "zone": random.choice(ZONES),
            "notes": random.choice(["", "Traffic delay", "Customer not available", "Wrong address", ""]),
        })

    with open(out_dir / "delivery_logs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✅ Generated {n} delivery log entries → {out_dir}/delivery_logs.csv")


def generate_sop_text(out_dir: Path):
    """Creates a plain-text SOP file (PDF generation requires extra deps)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sop_content = """LOGISTICS DELIVERY MANAGEMENT - STANDARD OPERATING PROCEDURES
================================================================

1. SHIPMENT DELAY HANDLING
--------------------------
- A shipment is considered delayed if it exceeds its SLA deadline by more than 30 minutes.
- Delay thresholds:
    Level 1 (30–60 min): Driver to attempt re-delivery same day.
    Level 2 (60–120 min): Notify customer via SMS/email; log reason code.
    Level 3 (>120 min): Escalate to Delivery Manager; customer compensation eligible.
- Root causes must be logged: traffic, vehicle breakdown, wrong address, customer unavailable.

2. SLA BREACH PROTOCOL
----------------------
- SLA targets: Same Day = 12 hours, Standard = 48 hours, Economy = 72 hours.
- On SLA breach: Delivery Manager must receive an automated alert.
- Escalation path: Driver → Hub Supervisor → Delivery Manager → Regional Head.
- All breached shipments must be reattempted within 4 hours of breach detection.

3. FAILED DELIVERY HANDLING
----------------------------
- After 2 failed attempts, shipment is returned to hub.
- Customer must be contacted within 1 hour of failed attempt.
- A final delivery window of 48 hours is offered before return-to-origin.
- Failed delivery reason codes: FA01 (absent), FA02 (wrong address), FA03 (refused), FA04 (access denied).

4. DRIVER PERFORMANCE STANDARDS
--------------------------------
- Minimum on-time delivery rate: 90%
- Maximum allowed delay per shift: 3 delayed shipments
- Drivers below 85% on-time for 2 consecutive weeks are placed on Performance Improvement Plan (PIP).
- Top performers (>97% on-time) are eligible for monthly incentive.

5. ROUTE MANAGEMENT
--------------------
- Routes are reviewed weekly. High-delay routes are re-optimised by the Route Planning team.
- Zones with >10% SLA breach rate trigger an immediate zone audit.
- Route reassignments require 24-hour advance notice to the driver.

6. DAMAGE & RETURNS
--------------------
- Damaged shipments must be photographed before return.
- Damage report submitted via the portal within 2 hours.
- Customer refund initiated within 3 business days of confirmed damage.
"""
    sop_path = out_dir / "delivery_sop.txt"
    sop_path.write_text(sop_content, encoding="utf-8")
    print(f"  ✅ Generated SOP document → {sop_path}")
    print("  ℹ️  Note: Place real PDF SOPs in data/sops/ for production use.")


if __name__ == "__main__":
    base = Path("data")
    print("Generating sample logistics data...\n")
    generate_shipments(base / "shipments")
    generate_routes(base / "routes")
    generate_logs(base / "logs")
    generate_sop_text(base / "sops")
    print("\n✅ Sample data generation complete!")
    print("   Run `python ingest.py` next to build the vector store.")
