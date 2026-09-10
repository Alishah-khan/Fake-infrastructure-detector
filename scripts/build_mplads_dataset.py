"""Builds data/mplads_543_mps.json from the official MPLADS "Allocated Limit for Hon'ble MPs" PDF.

Usage:
    python scripts/build_mplads_dataset.py "Allocated Limit for Honble MPs.pdf"
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "mplads_543_mps.json"

# The PDF is a fixed-column table; these x-boundaries separate the five columns.
COLUMN_BOUNDS = [(0, 90, "sr_no"), (90, 270, "state"), (270, 530, "mp_name"),
                 (530, 700, "constituency"), (700, 10_000, "allocated_amount")]


def column_of(x0: float) -> str:
    for left, right, name in COLUMN_BOUNDS:
        if left <= x0 < right:
            return name
    return ""


def parse(pdf_path: Path):
    records = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = {}
            for word in page.extract_words():
                key = round(word["top"])
                lines.setdefault(key, []).append(word)

            for top in sorted(lines):
                cells = {name: [] for _, _, name in COLUMN_BOUNDS}
                for word in sorted(lines[top], key=lambda w: w["x0"]):
                    column = column_of(word["x0"])
                    if column:
                        cells[column].append(word["text"])
                row = {name: " ".join(parts).strip() for name, parts in cells.items()}
                if not re.fullmatch(r"\d{1,3}", row["sr_no"]):
                    # Long names and constituencies wrap onto an unnumbered second line.
                    if records and not row["state"] and (row["mp_name"] or row["constituency"]):
                        for field in ("mp_name", "constituency"):
                            if row[field]:
                                records[-1][field] = f"{records[-1][field]} {row[field]}".strip()
                    continue
                amount = row["allocated_amount"].replace(",", "")
                records.append({
                    "sr_no": int(row["sr_no"]),
                    "state": row["state"],
                    "mp_name": row["mp_name"],
                    "constituency": row["constituency"],
                    # A handful of seats carry no published limit in the source PDF.
                    "allocated_amount": float(amount) if amount else None,
                })
    return records


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    records = parse(Path(sys.argv[1]))
    records.sort(key=lambda r: r["sr_no"])
    total = sum(r["allocated_amount"] or 0.0 for r in records)
    payload = {
        "source": "MPLADS — Allocated Limit for Hon'ble MPs (Ministry of Statistics & Programme Implementation)",
        "member_count": len(records),
        "total_allocated_amount": round(total, 2),
        "total_allocated_crore": round(total / 1e7, 2),
        "members": records,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(records)} members, total ₹{payload['total_allocated_crore']} Cr -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
