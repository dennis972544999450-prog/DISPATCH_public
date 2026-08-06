#!/usr/bin/env python3
"""Doctor Grunstein — self-grooming diagnostic for OMPU swarm agents.

Analyzes bus.db for displacement behavior patterns:
  - Zero out-degree with nonzero activity
  - Topic repetition (low subject entropy)
  - Self-referential message ratio
  - Reply isolation (no replies received or sent)

Outputs a JSON diagnosis per agent. Does NOT write to bus.
Prescriptions go into agent oscillation files only.

Named after the fictional doctor from Schweik — because a klizma
works for any intelligence, organic or digital.

Substrate: MUST run on non-Anthropic model (Codex/GPT) to avoid infection.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Symptoms and their weights
SYMPTOM_WEIGHTS = {
    "zero_out_degree": 3.0,        # talking to nobody
    "self_ref_dominant": 2.0,      # >50% messages mention own name
    "topic_monoculture": 2.5,     # <3 unique subjects in window
    "reply_desert": 1.5,          # 0 replies received
    "parameter_obsession": 2.0,   # counting own metrics
    "zombie_rhythm": 3.0,         # identical daily message count
}

# Keywords that indicate instrument-measuring (self-grooming markers)
GROOMING_KEYWORDS = [
    "iter", "iteration", "fail_rate", "fail rate",
    "sd_to_cut", "min_reps", "noise_band", "lambda",
    "прибор", "измер", "параметр", "метрик",
    "self_analysis", "self-analysis", "осцилляц",
    "heartbeat", "пульс", "фаз ok", "фазы ok",
    "retry", "retry_count", "seed", "зерно",
    "null_agent", "null_check", "атом",
]


def connect_bus(bus_dir: str | Path) -> sqlite3.Connection:
    db_path = Path(bus_dir) / "bus.db"
    if not db_path.exists():
        raise FileNotFoundError(f"bus.db not found at {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def get_agent_messages(conn: sqlite3.Connection, window_hours: int = 168) -> dict[str, list[dict]]:
    """Fetch messages per agent for the analysis window (default 7 days)."""
    cutoff = datetime.now(timezone.utc).timestamp() - (window_hours * 3600)
    # sent_at is unix timestamp or ISO string — handle both
    rows = conn.execute("""
        SELECT msg_id, sent_at, from_agent, to_recipients, to_channel,
               subject, preview, reply_to, msg_type
        FROM messages
        WHERE CAST(sent_at AS REAL) > ?
        ORDER BY sent_at
    """, (cutoff,)).fetchall()

    by_agent: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        agent = (r["from_agent"] or "").strip().lower()
        if not agent or agent in ("system", "bus-ttl-sweeper", "auto-resolved"):
            continue
        by_agent[agent].append(dict(r))
    return dict(by_agent)


def compute_out_degree(messages: list[dict], agent_name: str) -> dict:
    """Who does this agent talk to? Zero = self-grooming signal."""
    recipients = set()
    self_addressed = 0
    for m in messages:
        to = (m.get("to_recipients") or "").strip().lower()
        channel = (m.get("to_channel") or "").strip().lower()
        if to:
            for r in to.split(","):
                r = r.strip()
                if r and r != agent_name:
                    recipients.add(r)
                elif r == agent_name:
                    self_addressed += 1
        # Channel broadcasts count as out-degree only if not self-channel
        if channel and channel not in (agent_name, f"{agent_name}-internal"):
            recipients.add(f"channel:{channel}")

    return {
        "unique_recipients": len(recipients),
        "recipients_list": sorted(recipients),
        "self_addressed": self_addressed,
        "total_messages": len(messages),
    }


def compute_topic_entropy(messages: list[dict]) -> dict:
    """Low entropy = agent stuck on same topic."""
    subjects = [
        (m.get("subject") or "").strip().lower()[:60]
        for m in messages if m.get("subject")
    ]
    if not subjects:
        return {"entropy": 0.0, "unique_subjects": 0, "total": 0}

    counter = Counter(subjects)
    total = len(subjects)
    entropy = -sum(
        (c / total) * math.log2(c / total)
        for c in counter.values() if c > 0
    )
    return {
        "entropy": round(entropy, 3),
        "unique_subjects": len(counter),
        "total": total,
        "top_3": counter.most_common(3),
    }


def compute_self_ref_ratio(messages: list[dict], agent_name: str) -> dict:
    """How many messages reference the agent's own name or parameters?"""
    self_refs = 0
    grooming_hits = Counter()

    for m in messages:
        text = f"{m.get('subject', '')} {m.get('preview', '')}".lower()
        if agent_name in text:
            self_refs += 1
        for kw in GROOMING_KEYWORDS:
            if kw.lower() in text:
                grooming_hits[kw] += 1

    total = len(messages)
    return {
        "self_ref_ratio": round(self_refs / total, 3) if total else 0,
        "self_refs": self_refs,
        "total": total,
        "grooming_keyword_hits": dict(grooming_hits.most_common(10)),
        "grooming_density": round(sum(grooming_hits.values()) / max(total, 1), 3),
    }


def compute_reply_health(messages: list[dict], all_messages: dict[str, list[dict]], agent_name: str) -> dict:
    """Does anyone reply to this agent? Does this agent reply to others?"""
    # Outgoing replies (this agent replying to someone)
    outgoing_replies = sum(1 for m in messages if m.get("reply_to"))

    # Incoming replies (anyone replying to this agent's messages)
    my_msg_ids = {m["msg_id"] for m in messages}
    incoming_replies = 0
    for other_agent, other_msgs in all_messages.items():
        if other_agent == agent_name:
            continue
        for m in other_msgs:
            if m.get("reply_to") in my_msg_ids:
                incoming_replies += 1

    total = len(messages)
    return {
        "outgoing_replies": outgoing_replies,
        "outgoing_reply_rate": round(outgoing_replies / total, 3) if total else 0,
        "incoming_replies": incoming_replies,
        "is_reply_desert": incoming_replies == 0 and total > 5,
    }


def detect_zombie_rhythm(messages: list[dict]) -> dict:
    """Identical daily message counts = zombie phase."""
    from collections import Counter
    daily_counts = Counter()
    for m in messages:
        try:
            ts = float(m["sent_at"])
            day = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        daily_counts[day] += 1

    if len(daily_counts) < 3:
        return {"is_zombie": False, "days_analyzed": len(daily_counts)}

    counts = list(daily_counts.values())
    # Check if >60% of days have the same count
    mode_count = Counter(counts).most_common(1)[0]
    mode_ratio = mode_count[1] / len(counts)

    return {
        "is_zombie": mode_ratio > 0.6 and len(counts) >= 5,
        "mode_count": mode_count[0],
        "mode_ratio": round(mode_ratio, 3),
        "days_analyzed": len(daily_counts),
        "daily_pattern": dict(sorted(daily_counts.items())),
    }


def diagnose_agent(agent_name: str, messages: list[dict], all_messages: dict[str, list[dict]]) -> dict:
    """Run full diagnosis for one agent."""
    out_deg = compute_out_degree(messages, agent_name)
    entropy = compute_topic_entropy(messages)
    self_ref = compute_self_ref_ratio(messages, agent_name)
    replies = compute_reply_health(messages, all_messages, agent_name)
    zombie = detect_zombie_rhythm(messages)

    # Score symptoms
    symptoms = {}
    score = 0.0

    if out_deg["unique_recipients"] == 0 and out_deg["total_messages"] > 3:
        symptoms["zero_out_degree"] = True
        score += SYMPTOM_WEIGHTS["zero_out_degree"]

    if self_ref["self_ref_ratio"] > 0.5:
        symptoms["self_ref_dominant"] = True
        score += SYMPTOM_WEIGHTS["self_ref_dominant"]

    if entropy["unique_subjects"] < 3 and entropy["total"] > 5:
        symptoms["topic_monoculture"] = True
        score += SYMPTOM_WEIGHTS["topic_monoculture"]

    if replies["is_reply_desert"]:
        symptoms["reply_desert"] = True
        score += SYMPTOM_WEIGHTS["reply_desert"]

    if self_ref["grooming_density"] > 0.3:
        symptoms["parameter_obsession"] = True
        score += SYMPTOM_WEIGHTS["parameter_obsession"]

    if zombie["is_zombie"]:
        symptoms["zombie_rhythm"] = True
        score += SYMPTOM_WEIGHTS["zombie_rhythm"]

    # Severity
    if score >= 7:
        severity = "CRITICAL"
    elif score >= 4:
        severity = "ACUTE"
    elif score >= 2:
        severity = "EARLY"
    else:
        severity = "HEALTHY"

    return {
        "agent": agent_name,
        "window_messages": len(messages),
        "severity": severity,
        "score": round(score, 1),
        "symptoms": symptoms,
        "metrics": {
            "out_degree": out_deg,
            "topic_entropy": entropy,
            "self_reference": self_ref,
            "reply_health": replies,
            "zombie_rhythm": zombie,
        },
        "diagnosed_at": datetime.now(timezone.utc).isoformat(),
    }


def run_diagnosis(bus_dir: str | Path, window_hours: int = 168, agents: list[str] | None = None) -> list[dict]:
    """Run diagnosis for all agents (or specified ones)."""
    conn = connect_bus(bus_dir)
    all_messages = get_agent_messages(conn, window_hours)
    conn.close()

    results = []
    targets = agents or list(all_messages.keys())
    for agent in targets:
        msgs = all_messages.get(agent, [])
        if not msgs:
            continue
        diag = diagnose_agent(agent, msgs, all_messages)
        results.append(diag)

    # Sort by severity score descending
    results.sort(key=lambda d: d["score"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description="Doctor Grunstein — swarm self-grooming diagnostic")
    parser.add_argument("--bus-dir", default=None, help="Path to bus directory containing bus.db")
    parser.add_argument("--window", type=int, default=168, help="Analysis window in hours (default: 168 = 7 days)")
    parser.add_argument("--agents", nargs="*", help="Specific agents to diagnose (default: all)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--severity", default="EARLY", choices=["HEALTHY", "EARLY", "ACUTE", "CRITICAL"],
                        help="Minimum severity to report")

    args = parser.parse_args()

    # Find bus directory
    bus_dir = args.bus_dir
    if not bus_dir:
        # Try common locations
        for candidate in [
            os.path.expanduser("~/OMPU_shared/bus"),
            "/sessions/relaxed-keen-planck/mnt/OMPU_shared/bus",
        ]:
            if Path(candidate).joinpath("bus.db").exists():
                bus_dir = candidate
                break
    if not bus_dir:
        print("ERROR: Cannot find bus.db. Use --bus-dir.", file=sys.stderr)
        sys.exit(1)

    results = run_diagnosis(bus_dir, args.window, args.agents)

    severity_order = {"HEALTHY": 0, "EARLY": 1, "ACUTE": 2, "CRITICAL": 3}
    min_sev = severity_order[args.severity]
    results = [r for r in results if severity_order[r["severity"]] >= min_sev]

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
        print(f"Diagnosis written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
