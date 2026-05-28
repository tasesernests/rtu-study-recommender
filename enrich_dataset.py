#!/usr/bin/env python3
"""
enrich_dataset.py — Gemini-powered matching field enrichment for all 64 RTU programmes.

Reads each programme's name / description / goals / career info, asks Gemini to
return canonical matching tags + keywords, and writes them back to the source JSON.

Usage:
    python enrich_dataset.py               # enrich all programmes
    python enrich_dataset.py --dry-run     # preview without writing
    python enrich_dataset.py --force       # re-enrich already-done programmes
    python enrich_dataset.py --file rtu_programs.json   # one file only

Requires GEMINI_API_KEY in environment or .env file.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    print("ERROR: GEMINI_API_KEY is not set. Add it to your .env file or environment.")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    print("ERROR: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL VOCABULARY  (must exactly match utils.py keys)
# ─────────────────────────────────────────────────────────────────────────────

DOMAINS = {
    "it_programming":             "IT, computer science, programming, cybersecurity, networking, databases",
    "data_science_ai":            "Data science, artificial intelligence, machine learning, analytics, statistics",
    "software_engineering":       "Software engineering, software development, DevOps, system architecture",
    "electronics_telecom":        "Electronics, circuits, telecommunications, embedded systems, signals, RF",
    "robotics_automation":        "Robotics, automation, mechatronics, control systems, CNC",
    "mechanics_engineering":      "Mechanical engineering, machines, manufacturing, metal processing, CAD/CAM",
    "energy_power":               "Electrical engineering, power systems, smart grids, HVAC, renewable energy, heat",
    "transport_aviation":         "Transport, aviation, automotive, aeronautics, logistics, drone, UAV",
    "construction_civil":         "Civil engineering, construction, infrastructure, structural engineering, bridges",
    "architecture":               "Architecture, urban planning, interior design, spatial design, BIM",
    "art_design":                 "Industrial design, graphic design, visual art, product design, creative media",
    "chemistry_biotech":          "Chemistry, biochemistry, biotechnology, materials science, polymer chemistry",
    "environment_sustainability": "Environmental science, ecology, sustainability, climate change, water",
    "maritime":                   "Maritime, marine engineering, navigation, ship engineering, naval",
    "business_management":        "Business, management, economics, finance, entrepreneurship, marketing, supply chain",
    "medical_technology":         "Biomedical engineering, medical physics, health technology, medical devices",
    "education_research":         "Scientific research, academia, pedagogy, education, social work, psychology",
}

STRENGTHS = {
    "mathematics":         "Mathematical aptitude, calculus, algebra, statistics",
    "physics":             "Physics, mechanics, thermodynamics, optics",
    "chemistry":           "Chemistry, lab work, chemical analysis",
    "biology":             "Biology, life sciences, microbiology",
    "programming":         "Programming, coding, software development",
    "creativity":          "Creative thinking, innovation, idea generation",
    "drawing_design":      "Drawing, sketching, visual design, CAD modelling",
    "languages":           "Foreign languages, English proficiency, multilingual communication",
    "analytical_thinking": "Analytical thinking, problem-solving, logical reasoning, critical thinking",
    "technical_thinking":  "Technical/engineering mindset, systems thinking",
    "communication":       "Communication, presentation, writing, interpersonal skills",
    "leadership":          "Leadership, organisation, project management, planning",
    "research":            "Research skills, data analysis, scientific methodology, experimentation",
    "practical_skills":    "Hands-on work, practical skills, craftsmanship, lab skills, workshop",
    "economics_finance":   "Economics, finance, accounting, business analysis",
    "social_sciences":     "Social sciences, psychology, sociology, human behaviour",
}

PERSONALITY = {
    "analytical":               "Logical, systematic, enjoys solving complex problems",
    "creative":                 "Creative, innovative, enjoys design and new ideas",
    "practical":                "Practical, hands-on, prefers tangible, concrete results",
    "scientific":               "Scientific mindset, enjoys theory, experiments and deep research",
    "social":                   "Social, enjoys working with people and helping others",
    "technical":                "Technical orientation, loves technology, machines and systems",
    "entrepreneurial":          "Entrepreneurial, initiative-taking, leadership and business focus",
    "independent":              "Self-directed, prefers working independently",
    "team_player":              "Collaborative, enjoys group work and teamwork",
    "precise":                  "Detail-oriented, precise, thorough, meticulous",
    "international":            "Interested in international environments and global perspective",
    "adventurous":              "Active, adventurous, thrives in field/dynamic/challenging conditions",
    "sustainability_conscious": "Environmentally conscious, values sustainability and social ethics",
}

# ─────────────────────────────────────────────────────────────────────────────
# GEMINI CLIENT
# ─────────────────────────────────────────────────────────────────────────────

_client = genai.Client(api_key=API_KEY)
_MODEL  = "gemini-2.5-flash"


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME INFO EXTRACTOR  (handles all 4 dataset formats)
# ─────────────────────────────────────────────────────────────────────────────

def _s(val) -> str:
    """Flatten any value to a plain string."""
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return val.get("lv", "") or val.get("en", "") or ""
    if isinstance(val, list):
        return "; ".join(str(v) for v in val if v)
    return str(val) if val else ""


def extract_info(prog: dict) -> dict:
    name_lv = (
        _s(prog.get("name") or prog.get("name_lv") or "")
        or prog.get("id", "?")
    )
    name_en = _s(prog.get("name_en") or
                 (prog.get("name", {}).get("en", "") if isinstance(prog.get("name"), dict) else ""))

    description = _s(prog.get("description", ""))

    goals_raw = prog.get("goals") or prog.get("goal") or ""
    if isinstance(goals_raw, list):
        goals = "; ".join(goals_raw[:3])
    else:
        goals = _s(goals_raw)

    study_dir = _s(prog.get("study_direction", ""))

    career = prog.get("career") or prog.get("career_prospects") or {}
    job_titles = (
        career.get("job_titles") or career.get("example_roles") or
        career.get("roles") or []
    )
    career_desc = career.get("description", "")

    return {
        "name_lv":       name_lv[:80],
        "name_en":       name_en[:80],
        "study_dir":     study_dir[:120],
        "description":   description[:500],
        "goals":         goals[:300],
        "job_titles":    job_titles[:7],
        "career_desc":   career_desc[:200],
    }


# ─────────────────────────────────────────────────────────────────────────────
# PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(info: dict) -> str:
    domain_block = "\n".join(
        f'  "{k}": {desc}' for k, desc in DOMAINS.items()
    )
    strength_block = "\n".join(
        f'  "{k}": {desc}' for k, desc in STRENGTHS.items()
    )
    personality_block = "\n".join(
        f'  "{k}": {desc}' for k, desc in PERSONALITY.items()
    )

    return f"""You are tagging an RTU (Riga Technical University) bachelor programme for a student recommendation system.

PROGRAMME:
Name (Latvian): {info["name_lv"]}
Name (English): {info["name_en"]}
Study direction: {info["study_dir"]}
Description: {info["description"]}
Goals: {info["goals"]}
Career roles: {", ".join(info["job_titles"])}
Career description: {info["career_desc"]}

CANONICAL DOMAIN KEYS — choose 3 to 5, most relevant first:
{domain_block}

CANONICAL STRENGTH KEYS — choose 4 to 7 that students in this programme need:
{strength_block}

CANONICAL PERSONALITY KEYS — choose 3 to 4 that fit students who thrive here:
{personality_block}

Return ONLY a valid JSON object (no markdown, no explanation):
{{
  "interest_domains": ["key1", "key2", "key3"],
  "required_strengths": ["key1", "key2", "key3", "key4"],
  "personality_fit": ["key1", "key2", "key3"],
  "keywords": ["keyword1", "keyword2", ...],
  "math_intensive": true or false,
  "creative_component": true or false,
  "research_oriented": true or false,
  "international_potential": true or false,
  "teamwork_oriented": true or false,
  "difficulty_level": "low" or "medium" or "medium_high" or "high"
}}

Constraints:
- Only use exact key strings shown above — no others allowed
- keywords: 10–15 short English career/study terms (e.g. "civil engineer", "data analyst", "ship captain")
- difficulty: "high" = heavy maths/physics/theory; "medium_high" = moderately demanding; "medium" = standard; "low" = accessible
- teamwork_oriented: true if the programme involves significant group projects / team collaboration"""


# ─────────────────────────────────────────────────────────────────────────────
# API CALL + VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def _parse_retry_delay(exc: Exception) -> float:
    """Extract retryDelay seconds from a 429 RESOURCE_EXHAUSTED error message."""
    msg = str(exc)
    # Handle both single- and double-quoted repr (Python dict str vs JSON)
    m = re.search(r"['\"]retryDelay['\"]\s*:\s*['\"](\d+(?:\.\d+)?)s['\"]", msg)
    if m:
        return min(float(m.group(1)) + 3.0, 65.0)
    # Fallback: wait a full minute to guarantee the RPM window resets
    return 65.0


def call_gemini(prompt: str, retries: int = 1) -> Optional[dict]:
    for attempt in range(retries + 1):
        try:
            response = _client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=700,
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                ),
            )
            text = (response.text or "").strip()
            # Strip markdown fences
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                return json.loads(m.group())
            print(f"      No JSON in response (attempt {attempt + 1}): {text[:80]}")
        except json.JSONDecodeError as e:
            print(f"      JSON parse error (attempt {attempt + 1}): {e}")
        except Exception as e:
            err_str = str(e)
            if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                wait = _parse_retry_delay(e)
                print(f"      Rate limited — waiting {wait:.0f}s before retry…")
                time.sleep(wait)
                continue  # one retry after waiting
            if "PERMISSION_DENIED" in err_str or "403" in err_str:
                print(f"      Permission denied — API key invalid or leaked. Aborting.")
                return None
            if "INVALID_ARGUMENT" in err_str or "400" in err_str:
                print(f"      Invalid request (400) — check API key. Aborting.")
                return None
            print(f"      API error (attempt {attempt + 1}): {err_str[:120]}")
        if attempt < retries:
            time.sleep(5)
    return None


def validate(raw: dict) -> dict:
    """Remove invalid keys and cap list lengths."""
    valid_d = set(DOMAINS)
    valid_s = set(STRENGTHS)
    valid_p = set(PERSONALITY)
    valid_diff = {"low", "medium", "medium_high", "high"}

    domains    = [k for k in raw.get("interest_domains",   []) if k in valid_d][:5]
    strengths  = [k for k in raw.get("required_strengths", []) if k in valid_s][:7]
    personality= [k for k in raw.get("personality_fit",    []) if k in valid_p][:4]
    keywords   = [str(k).strip() for k in raw.get("keywords", []) if k][:15]
    difficulty = raw.get("difficulty_level", "medium")
    if difficulty not in valid_diff:
        difficulty = "medium"

    return {
        "interest_domains":    domains,
        "required_strengths":  strengths,
        "personality_fit":     personality,
        "keywords":            keywords,
        "math_intensive":      bool(raw.get("math_intensive",       False)),
        "creative_component":  bool(raw.get("creative_component",   False)),
        "research_oriented":   bool(raw.get("research_oriented",    False)),
        "international_potential": bool(raw.get("international_potential", False)),
        "teamwork_oriented":   bool(raw.get("teamwork_oriented",    True)),
        "difficulty_level":    difficulty,
    }


# ─────────────────────────────────────────────────────────────────────────────
# FILE PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────

def process_file(path: Path, dry_run: bool, force: bool, delay: float) -> tuple[int, int]:
    """Enrich all programmes in one JSON file. Returns (enriched, skipped)."""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    key = "programs" if "programs" in data else "programmes"
    programs = data.get(key, [])
    if not programs:
        print("  No programmes list found.")
        return 0, 0

    enriched_count = 0
    skipped_count  = 0

    for i, prog in enumerate(programs):
        pid  = prog.get("id") or prog.get("slug") or f"#{i}"
        name = _s(prog.get("name") or prog.get("name_lv") or "")

        # Skip if already enriched (non-empty keywords present) unless --force
        if bool(prog.get("keywords")) and not force:
            print(f"  [{i+1:2}/{len(programs)}] SKIP {pid:<12} (already enriched)")
            skipped_count += 1
            continue

        print(f"  [{i+1:2}/{len(programs)}] {pid:<12} {name[:45]}")

        info   = extract_info(prog)
        prompt = build_prompt(info)
        raw    = call_gemini(prompt)

        if raw is None:
            print("             → FAILED — skipping")
            time.sleep(delay * 2)
            continue

        result = validate(raw)

        if len(result["interest_domains"]) < 2:
            print(f"             → WARN: only {len(result['interest_domains'])} valid domains")

        print(f"             domains:    {result['interest_domains']}")
        print(f"             strengths:  {result['required_strengths']}")
        print(f"             keywords:   {result['keywords'][:5]}{'…' if len(result['keywords']) > 5 else ''}")
        print(f"             flags:      math={result['math_intensive']} creative={result['creative_component']} "
              f"research={result['research_oriented']} intl={result['international_potential']} "
              f"team={result['teamwork_oriented']} diff={result['difficulty_level']}")

        if not dry_run:
            existing = prog.get("matching", {}) or {}
            existing.update({
                "interest_domains":        result["interest_domains"],
                "required_strengths":      result["required_strengths"],
                "personality_fit":         result["personality_fit"],
                "math_intensive":          result["math_intensive"],
                "creative_component":      result["creative_component"],
                "research_oriented":       result["research_oriented"],
                "international_potential": result["international_potential"],
                "teamwork_oriented":       result["teamwork_oriented"],
                "difficulty_level":        result["difficulty_level"],
            })
            prog["matching"]  = existing
            prog["keywords"]  = result["keywords"]

        enriched_count += 1
        time.sleep(delay)

    if not dry_run and enriched_count > 0:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n  ✓ Saved {enriched_count} programmes → {path.name}")

    return enriched_count, skipped_count


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Enrich RTU dataset matching fields using Gemini AI."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without modifying files")
    parser.add_argument("--force",   action="store_true",
                        help="Re-enrich even if keywords already present")
    parser.add_argument("--delay",   type=float, default=13.0,
                        help="Seconds between Gemini API calls (default 13 — safe for free-tier 5 RPM)")
    parser.add_argument("--file",    type=str, default=None,
                        help="Process only this filename (e.g. rtu_programs.json)")
    args = parser.parse_args()

    dataset_dir = Path(__file__).parent / "datasets"
    if not dataset_dir.exists():
        print(f"ERROR: datasets/ directory not found at {dataset_dir}")
        sys.exit(1)

    if args.dry_run:
        print("=" * 64)
        print("DRY RUN — no files will be written")
        print("=" * 64)

    files = (
        [dataset_dir / args.file] if args.file
        else sorted(dataset_dir.glob("*.json"))
    )

    total_enriched = 0
    total_skipped  = 0

    for path in files:
        if not path.exists():
            print(f"ERROR: {path} not found")
            continue
        size_kb = path.stat().st_size // 1024
        print(f"\n{'='*64}")
        print(f"  {path.name}  ({size_kb} KB)")
        print(f"{'='*64}")
        e, s = process_file(path, args.dry_run, args.force, args.delay)
        total_enriched += e
        total_skipped  += s

    print(f"\n{'='*64}")
    print(f"  Enriched: {total_enriched}   Skipped (already done): {total_skipped}")
    if args.dry_run:
        print("  (DRY RUN — no files were modified)")
    else:
        print("  Run 'streamlit run app.py' to see the improved recommendations.")
    print(f"{'='*64}")


if __name__ == "__main__":
    main()
