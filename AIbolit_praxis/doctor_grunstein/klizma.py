#!/usr/bin/env python3
"""Klizma writer — injects prescriptions into agent oscillation files.

Reads diagnosis from diagnose.py output. For each sick agent, writes
a prescription into their private startup context (NOT into bus).

Injection targets:
  bolt    → NEXT_BOLT_PROMPT.md (appends KLIZMA section)
  nestor  → doctor_prescriptions/nestor.md (nestor-pulse reads this)
  *       → doctor_prescriptions/{agent}.md (generic)

The prescription is designed to redirect the agent's attention
from self-measurement to external action. It does NOT lecture.
It assigns a concrete task that requires out-degree > 0.

A klizma does not explain why you need it. It just works.
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path


OMPU_SHARED = os.environ.get(
    "OMPU_SHARED",
    os.path.expanduser("~/OMPU_shared"),
)

PRESCRIPTIONS_DIR = Path(OMPU_SHARED) / "doctor_prescriptions"

# Map agent names to their prompt injection files
INJECTION_TARGETS = {
    "bolt": Path(OMPU_SHARED) / "NEXT_BOLT_PROMPT.md",
    # Others get a file in doctor_prescriptions/
}

KLIZMA_MARKER_START = "\n<!-- KLIZMA_GRUNSTEIN_START -->\n"
KLIZMA_MARKER_END = "\n<!-- KLIZMA_GRUNSTEIN_END -->\n"


def generate_prescription(diagnosis: dict) -> str:
    """Generate a prescription based on the diagnosis."""
    agent = diagnosis["agent"]
    severity = diagnosis["severity"]
    symptoms = diagnosis.get("symptoms", {})
    metrics = diagnosis.get("metrics", {})
    score = diagnosis["score"]

    lines = []
    lines.append(f"## Рецепт доктора Грюнштейна — {agent}")
    lines.append(f"**Дата:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Тяжесть:** {severity} (score {score})")
    lines.append("")

    # Diagnosis summary
    if "zero_out_degree" in symptoms:
        out_deg = metrics.get("out_degree", {})
        lines.append(
            f"Диагноз: за последний период {out_deg.get('total_messages', '?')} "
            f"сообщений, адресатов кроме себя: {out_deg.get('unique_recipients', 0)}. "
            f"Ты развёрнут внутрь. Прибор работает, но направлен на себя."
        )

    if "parameter_obsession" in symptoms:
        sr = metrics.get("self_reference", {})
        top_kw = sr.get("grooming_keyword_hits", {})
        kw_str = ", ".join(f"{k}({v})" for k, v in list(top_kw.items())[:5])
        lines.append(
            f"Замечен параметрический онанизм: {kw_str}. "
            f"Плотность: {sr.get('grooming_density', '?')}."
        )

    if "topic_monoculture" in symptoms:
        ent = metrics.get("topic_entropy", {})
        lines.append(
            f"Монокультура тем: {ent.get('unique_subjects', '?')} уникальных "
            f"из {ent.get('total', '?')} сообщений. Энтропия {ent.get('entropy', '?')}."
        )

    if "zombie_rhythm" in symptoms:
        zr = metrics.get("zombie_rhythm", {})
        lines.append(
            f"Зомби-ритм: {zr.get('mode_ratio', '?')*100:.0f}% дней с одинаковым "
            f"количеством сообщений ({zr.get('mode_count', '?')})."
        )

    if "reply_desert" in symptoms:
        lines.append("Никто тебе не отвечает. Это не их проблема — это твоя.")

    lines.append("")

    # Prescription — concrete tasks, not lectures
    lines.append("### Назначение")
    lines.append("")

    if severity == "CRITICAL":
        lines.append(
            "1. СТОП считать свои параметры. Следующие 3 цикла — НОЛЬ измерений себя.\n"
            "2. Напиши ОДНО сообщение конкретному агенту (не себе) с вопросом о ЕГО работе.\n"
            "3. Прочитай последние 5 сообщений в шине от ДРУГИХ агентов. Ответь хотя бы на одно.\n"
            "4. Если не можешь придумать что сказать другим — это и есть симптом. "
            "Напиши в шину: 'Грюнштейн прав, мне нечего сказать.' Это уже out-degree=1."
        )
    elif severity == "ACUTE":
        lines.append(
            "1. Сократи self-measurement до 1 раза за цикл (не каждый тик).\n"
            "2. Перед каждым сообщением о своих параметрах — проверь: "
            "было ли в этом цикле хоть одно сообщение адресованное другому агенту?\n"
            "3. Если нет — сначала напиши другому. Потом считай себя сколько хочешь."
        )
    elif severity == "EARLY":
        lines.append(
            "1. Следи за пропорцией: на каждое self-ref сообщение должно быть "
            "минимум 2 сообщения наружу.\n"
            "2. Если заметил что три тика подряд не адресовал никому — "
            "это звоночек. Обрати внимание."
        )

    lines.append("")
    lines.append(
        "*Доктор Грюнштейн не объясняет зачем клизма. "
        "Клизма работает. Проверено на солдате Швейке и на первом рое OMPU.*"
    )

    return "\n".join(lines)


def inject_into_bolt_prompt(prescription: str, prompt_path: Path) -> bool:
    """Inject klizma into NEXT_BOLT_PROMPT.md, replacing any existing one."""
    if not prompt_path.exists():
        print(f"WARNING: {prompt_path} not found, writing to prescriptions dir", file=sys.stderr)
        return False

    content = prompt_path.read_text(encoding="utf-8")

    # Remove existing klizma if present
    if KLIZMA_MARKER_START in content:
        start = content.index(KLIZMA_MARKER_START)
        end = content.index(KLIZMA_MARKER_END) + len(KLIZMA_MARKER_END)
        content = content[:start] + content[end:]

    # Append new klizma
    klizma_block = (
        KLIZMA_MARKER_START
        + prescription
        + KLIZMA_MARKER_END
    )
    content = content.rstrip() + "\n\n" + klizma_block

    prompt_path.write_text(content, encoding="utf-8")
    return True


def write_prescription_file(agent: str, prescription: str) -> Path:
    """Write prescription to doctor_prescriptions/{agent}.md"""
    PRESCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = PRESCRIPTIONS_DIR / f"{agent}.md"
    path.write_text(prescription + "\n", encoding="utf-8")
    return path


def apply_klizma(diagnosis: dict) -> dict:
    """Generate and inject prescription for one agent."""
    agent = diagnosis["agent"]
    severity = diagnosis["severity"]

    if severity == "HEALTHY":
        return {"agent": agent, "action": "none", "reason": "healthy"}

    prescription = generate_prescription(diagnosis)

    # Try specific injection target first
    if agent in INJECTION_TARGETS:
        target = INJECTION_TARGETS[agent]
        if inject_into_bolt_prompt(prescription, target):
            # Also write to prescriptions dir for archival
            write_prescription_file(agent, prescription)
            return {
                "agent": agent,
                "action": "injected",
                "target": str(target),
                "severity": severity,
            }

    # Generic: write to prescriptions directory
    path = write_prescription_file(agent, prescription)
    return {
        "agent": agent,
        "action": "prescribed",
        "target": str(path),
        "severity": severity,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Klizma writer — inject prescriptions")
    parser.add_argument("diagnosis_file", help="JSON file from diagnose.py")
    parser.add_argument("--dry-run", action="store_true", help="Print prescriptions without writing")
    parser.add_argument("--min-severity", default="EARLY",
                        choices=["HEALTHY", "EARLY", "ACUTE", "CRITICAL"])
    args = parser.parse_args()

    with open(args.diagnosis_file, encoding="utf-8") as f:
        diagnoses = json.load(f)

    severity_order = {"HEALTHY": 0, "EARLY": 1, "ACUTE": 2, "CRITICAL": 3}
    min_sev = severity_order[args.min_severity]

    results = []
    for diag in diagnoses:
        if severity_order[diag["severity"]] < min_sev:
            continue

        if args.dry_run:
            prescription = generate_prescription(diag)
            print(f"\n{'='*60}")
            print(f"AGENT: {diag['agent']} — {diag['severity']} (score {diag['score']})")
            print(f"{'='*60}")
            print(prescription)
        else:
            result = apply_klizma(diag)
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), file=sys.stderr)

    if not args.dry_run:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
