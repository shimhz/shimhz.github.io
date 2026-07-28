#!/usr/bin/env python3
"""Fetch total citation count from Google Scholar and update files/scholar.json.

Exits 0 without touching the file when Scholar can't be parsed (e.g. the
request was blocked), so the workflow never overwrites a good value with
a bad one.
"""
import datetime
import json
import pathlib
import re
import sys
import urllib.request

URL = "https://scholar.google.com/citations?user=MSIvlNoAAAAJ&hl=en"
OUT = pathlib.Path(__file__).resolve().parent.parent / "files" / "scholar.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

try:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
except Exception as e:  # noqa: BLE001
    print(f"Fetch failed ({e}); keeping previous value.")
    sys.exit(0)

# Profile stats table cells in order: citations all/since, h-index all/since, i10 all/since
nums = re.findall(r'class="gsc_rsb_std">([\d,]+)</td>', html)
if not nums:
    print("Could not parse citation count (blocked?); keeping previous value.")
    sys.exit(0)

citations = int(nums[0].replace(",", ""))
hindex = int(nums[2].replace(",", "")) if len(nums) > 2 else None

old = {}
if OUT.exists():
    try:
        old = json.loads(OUT.read_text())
    except json.JSONDecodeError:
        pass

if old.get("citations") == citations and old.get("hindex") == hindex:
    print(f"Unchanged: {citations} citations.")
    sys.exit(0)

OUT.write_text(
    json.dumps(
        {
            "citations": citations,
            "hindex": hindex,
            "updated": datetime.date.today().isoformat(),
        }
    )
    + "\n"
)
print(f"Updated: {old.get('citations')} -> {citations} citations.")
