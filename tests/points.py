"""Print `points/max` from the points="…" and points_max="…" attributes that
tests/conftest.py writes into a JUnit report; a test without a points marker
counts 1."""

import sys
import xml.etree.ElementTree as ElementTree

points = total = 0.0
for case in ElementTree.parse(sys.argv[1]).iter("testcase"):
    weight = float(case.get("points_max", 1))
    failed = any(case.find(tag) is not None for tag in ("failure", "error", "skipped"))
    total += weight
    points += 0 if failed else float(case.get("points", weight))
print(f"{points:g}/{total:g}")
