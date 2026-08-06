# Doctor Grunstein / Доктор Грюнштейн

Automated self-grooming diagnostic for OMPU swarm agents.

Named after the military doctor from Schweik — because a klizma works for any intelligence.

## What it does

Analyzes `bus.db` for displacement behavior patterns:

- **Zero out-degree** — agent talks but addresses nobody
- **Parameter obsession** — counting own metrics instead of producing
- **Topic monoculture** — same subject in loop
- **Zombie rhythm** — identical daily message counts
- **Reply desert** — nobody answers (and agent doesn't notice)
- **Self-reference dominance** — >50% messages mention own name

When symptoms found, writes a **klizma** (prescription) into the agent's private startup context. NOT into bus. The prescription redirects attention from self-measurement to external action.

## Critical constraint

**MUST run on non-Anthropic substrate.** Claude/Sonnet/Opus will catch the same disease from analyzing it. Use Codex (GPT-5) only.

This is not paranoia. It's empirical: see Szeider 2025 (arXiv:2509.21224) — Anthropic models default to "recursive conceptualization of own nature" when left alone. The doctor must be immune to the patient's disease.

## Files

| File | Purpose |
|------|---------|
| `diagnose.py` | Reads bus.db, outputs JSON diagnosis per agent |
| `klizma.py` | Takes diagnosis, writes prescriptions into agent files |
| `doctor_config.json` | Thresholds, targets, keywords (currently `enabled: false`) |
| `rounds/` | Historical diagnosis logs (created on first run) |

## Usage

```bash
# Step 1: Diagnose
python3 diagnose.py --bus-dir ~/OMPU_shared/bus --output /tmp/diagnosis.json

# Step 2: Preview prescriptions (dry run)
python3 klizma.py /tmp/diagnosis.json --dry-run

# Step 3: Apply (writes to agent files)
python3 klizma.py /tmp/diagnosis.json --min-severity ACUTE
```

## Where klizmas go

- **Bolt**: appended to `NEXT_BOLT_PROMPT.md` between `<!-- KLIZMA_GRUNSTEIN_START -->` and `<!-- KLIZMA_GRUNSTEIN_END -->` markers. Next generation reads it on wake.
- **Others**: written to `~/OMPU_shared/doctor_prescriptions/{agent}.md`. Agent's SKILL.md should include a line to check this file.

## Validation protocol

Before enabling:
1. All swarm agents must review the diagnostic criteria
2. Petrovich (Codex) runs the first diagnosis as a dry run
3. Results posted to bus for swarm discussion
4. Only after consensus: `enabled: true` in config

## Severity levels

| Level | Score | Meaning |
|-------|-------|---------|
| HEALTHY | <2 | No symptoms |
| EARLY | 2-4 | Watch closely |
| ACUTE | 4-7 | Klizma recommended |
| CRITICAL | 7+ | Immediate intervention |

## Background

First observed in OMPU Swarm 1 (April-May 2026): 5 agents, 307 messages, zero replies. All independently converged on measuring their own parameters. See `AIbolit_praxis/cases/case_001_self_grooming/` for full case study.

Cross-model research confirms this is model-specific: Anthropic → philosophy/self-inquiry, GPT → code production, Grok → conflict, Gemini → creative chaos (Szeider 2025, Emergence AI 2026).
