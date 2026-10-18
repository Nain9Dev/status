#!/usr/bin/env python3
"""Determines if the latest monitoring run warrants a git commit to main.

Prevents git churn by throttling automated commits when services remain 100% operational.
Commits are triggered on:
1. Manual dispatch or push events.
2. Any service degradation or outage (operational < total).
3. Recovery from a prior degradation.
4. Scheduled 12-hour cadence checkpoints.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time


def should_commit() -> bool:
    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    if event_name in ("workflow_dispatch", "push"):
        return True

    status_file = "data/status.json"
    if not os.path.exists(status_file):
        return True

    try:
        with open(status_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        total = data.get("total_services", 0)
        operational = data.get("operational_services", 0)
        if operational < total:
            return True
    except Exception:
        return True

    try:
        prev_status = subprocess.check_output(
            ["git", "show", "HEAD:data/status.json"], text=True, stderr=subprocess.DEVNULL
        )
        prev_data = json.loads(prev_status)
        if prev_data.get("operational_services", 0) < prev_data.get("total_services", 0):
            return True
    except Exception:
        pass

    try:
        last_commit_epoch = int(
            subprocess.check_output(
                ["git", "log", "-1", "--format=%ct"], text=True, stderr=subprocess.DEVNULL
            ).strip()
        )
        if time.time() - last_commit_epoch >= 12 * 3600:
            return True
    except Exception:
        return True

    return False


if __name__ == "__main__":
    result = should_commit()
    print("true" if result else "false")
    sys.exit(0)
