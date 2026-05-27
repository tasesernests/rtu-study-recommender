"""
RTU Study Programme AI Recommender
data_loader.py — Robust multi-format JSON dataset loader and normalizer.

Handles all 4 known RTU dataset schemas:
  - rtu_programs.json          → Format A (main academic)
  - rtu_bmf_programs.json      → Format B (BMF professional)
  - rtu_programs_DITEF_IVF_*   → Format C (DITEF/IVF with matching_profile)
  - rtu_programs_rezekne_*     → Format D (RTU academies with recommendation_metadata)
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from utils import (
    DOMAIN_MAP, STRENGTH_MAP, PERSONALITY_MAP, SECTOR_MAP,
    map_to_canonical_domain, map_to_canonical_strength,
    map_to_canonical_personality, map_to_canonical_sector,
    map_tags, normalize_languages, normalize_difficulty,
    safe_get, coerce_int, coerce_float, flatten_str,
    extract_budget_places, extract_fee, extract_duration,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")
logger = logging.getLogger("data_loader")

# ── Default dataset locations (tried in order) ───────────────────────────────
_DEFAULT_DIRS = [
    Path(__file__).parent / "datasets",
    Path(os.environ.get("RTU_DATASET_DIR", "datasets")),
]


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def load_all_programmes(dataset_dir: Optional[Path] = None) -> tuple[list[dict], dict]:
    """
    Load and normalise all programmes from all JSON files in the dataset directory.

    Returns:
        (programmes, stats) where programmes is a list of normalised dicts
        and stats contains load diagnostics.
    """
    dirs_to_try = [dataset_dir] if dataset_dir else _DEFAULT_DIRS
    dataset_path = None
    for d in dirs_to_try:
        if d and Path(d).exists():
            dataset_path = Path(d)
            break

    if dataset_path is None:
        logger.error("No dataset directory found. Create a 'datasets/' folder and add JSON files.")
        return [], {"files_loaded": 0, "files_failed": 0, "total": 0}

    json_files = sorted(dataset_path.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files in {dataset_path}")
        return [], {"files_loaded": 0, "files_failed": 0, "total": 0}

    all_programmes: list[dict] = []
    stats = {"files_loaded": 0, "files_failed": 0, "total": 0, "by_file": {}}

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8-sig") as fh:
                data = json.load(fh)
            programmes = _parse_json_file(data, source_file=jf.name)
            all_programmes.extend(programmes)
            stats["files_loaded"] += 1
            stats["by_file"][jf.name] = len(programmes)
            logger.info(f"  ✓ {jf.name} → {len(programmes)} programmes")
        except json.JSONDecodeError as e:
            logger.warning(f"  ✗ {jf.name} — JSON parse error: {e}")
            stats["files_failed"] += 1
        except Exception as e:
            logger.warning(f"  ✗ {jf.name} — Error: {e}", exc_info=True)
            stats["files_failed"] += 1

    stats["total"] = len(all_programmes)
    logger.info(f"Dataset loaded: {stats['total']} programmes from {stats['files_loaded']} files")
    return all_programmes, stats


def extract_taxonomy(programmes: list[dict]) -> dict:
    """
    Extract a unified taxonomy summary from all loaded programmes.
    Useful for debug / UI population.
    """
    domains: set[str] = set()
    strengths: set[str] = set()
    personalities: set[str] = set()
    sectors: set[str] = set()
    faculties: set[str] = set()
    languages: set[str] = set()
    locations: set[str] = set()

    for p in programmes:
        m = p.get("matching", {}) or {}
        domains.update(m.get("interest_domains", []))
        strengths.update(m.get("required_strengths", []))
        personalities.update(m.get("personality_fit", []))
        sectors.update(p.get("career", {}).get("sectors_canonical", []))
        faculties.add(p.get("faculty", ""))
        languages.update(m.get("language_codes", []))
        locations.update(p.get("locations", []))

    return {
        "interest_domains": sorted(d for d in domains if d),
        "strength_tags": sorted(s for s in strengths if s),
        "personality_fit": sorted(p for p in personalities if p),
        "industry_sectors": sorted(s for s in sectors if s),
        "faculties": sorted(f for f in faculties if f),
        "languages": sorted(l for l in languages if l),
        "locations": sorted(loc for loc in locations if loc),
    }


def validate_programme(prog: dict) -> bool:
    """Return True if the normalised programme has the minimum required fields."""
    return bool(prog.get("name") and prog.get("faculty"))


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL: FILE-LEVEL DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json_file(data: dict, source_file: str) -> list[dict]:
    """Detect file format and extract programme list."""
    # Programmes key — some files use "programs", one might differ
    raw_list = data.get("programs") or data.get("programmes") or []

    if not isinstance(raw_list, list) or not raw_list:
        logger.warning(f"  {source_file}: no 'programs' list found")
        return []

    fmt = _detect_format(source_file, data, raw_list[0] if raw_list else {})
    logger.info(f"    Format detected: {fmt}")

    normalised = []
    for raw_prog in raw_list:
        if not isinstance(raw_prog, dict):
            continue
        try:
            prog = _normalise(raw_prog, source_file, fmt)
            if prog and validate_programme(prog):
                normalised.append(prog)
        except Exception as e:
            pid = raw_prog.get("id", "?")
            logger.debug(f"    Skipped programme {pid} in {source_file}: {e}")

    return normalised


def _detect_format(source_file: str, data: dict, sample_prog: dict) -> str:
    """Infer which normaliser to use based on filename + data structure."""
    name_lower = source_file.lower()
    if "bmf" in name_lower:
        return "bmf"
    if "ditef" in name_lower or "ivf" in name_lower:
        return "ditef"
    if any(k in name_lower for k in ("rezekne", "liepaja", "jura", "akademija")):
        return "rezekne"
    # Structure-based fallback
    if "matching_profile" in sample_prog:
        return "ditef"
    if "recommendation_metadata" in sample_prog or "institution" in sample_prog:
        return "rezekne"
    if sample_prog.get("faculty_short"):
        return "bmf"
    return "academic"  # main rtu_programs.json style


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL: UNIVERSAL NORMALISER (routes to format-specific helpers)
# ─────────────────────────────────────────────────────────────────────────────

def _normalise(raw: dict, source_file: str, fmt: str) -> Optional[dict]:
    if fmt == "bmf":
        return _norm_bmf(raw, source_file)
    if fmt == "ditef":
        return _norm_ditef(raw, source_file)
    if fmt == "rezekne":
        return _norm_rezekne(raw, source_file)
    return _norm_academic(raw, source_file)


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT A — rtu_programs.json (main academic)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_academic(r: dict, src: str) -> dict:
    logistics = r.get("logistics", {}) or {}
    finances = r.get("finances", {}) or {}
    admission = r.get("admission", {}) or {}
    degree = r.get("degree", {}) or {}
    career = r.get("career", {}) or {}
    matching_raw = r.get("matching", {}) or {}

    languages_raw = logistics.get("language") or logistics.get("languages") or []
    lang_codes = normalize_languages(languages_raw)

    budget = extract_budget_places(finances.get("budget_places"))
    fee = extract_fee(finances.get("annual_fee_eur"))
    duration = extract_duration(logistics.get("duration_years"))

    entry_exam = bool(admission.get("entry_exam") or admission.get("requires_entrance_exam", False))
    exam_details = admission.get("entry_exam_details") or ""

    # Canonical matching
    raw_domains = matching_raw.get("interest_domains", [])
    raw_strengths = matching_raw.get("required_strengths", [])
    raw_personalities = matching_raw.get("personality_fit", [])
    raw_lang = matching_raw.get("language_of_instruction", [])
    raw_sectors = career.get("sectors", [])

    sectors_canonical = map_tags(raw_sectors, map_to_canonical_sector)

    match_langs = normalize_languages(raw_lang) if raw_lang else lang_codes

    prog_dir = r.get("program_director", {}) or {}
    director_str = f"{prog_dir.get('name', '')} — {prog_dir.get('title', '')}".strip(" —")

    return {
        "id": r.get("id", ""),
        "name": r.get("name", ""),
        "name_en": r.get("name_en", ""),
        "faculty": r.get("faculty", ""),
        "faculty_short": r.get("faculty_short", ""),
        "program_type": r.get("program_type", ""),
        "study_direction": r.get("study_direction", ""),
        "study_field": r.get("study_field", ""),
        "degree": {
            "title": flatten_str(degree.get("title", "")),
            "title_en": flatten_str(degree.get("title_en", "")),
            "level": coerce_int(degree.get("level", 6)),
            "professional_qualification": degree.get("professional_qualification"),
        },
        "duration_years": duration,
        "credits": coerce_int(r.get("credits") or logistics.get("credits", 0) or 0) or 240,
        "format": logistics.get("format") or ", ".join(logistics.get("formats", ["Pilna laika"])),
        "languages": lang_codes,
        "locations": logistics.get("locations") or [logistics.get("start_location", "Rīga")],
        "budget_places": budget,
        "annual_fee_eur": fee,
        "entry_exam": entry_exam,
        "entry_exam_details": exam_details,
        "description": r.get("description", ""),
        "goals": flatten_str(r.get("goals", "")),
        "url": r.get("url"),
        "program_director": director_str,
        "career": {
            "description": career.get("description", ""),
            "job_titles": career.get("job_titles", []),
            "sectors": raw_sectors,
            "sectors_canonical": sectors_canonical,
        },
        "keywords": [],
        "source_file": src,
        "matching": {
            "interest_domains": map_tags(raw_domains, map_to_canonical_domain),
            "required_strengths": map_tags(raw_strengths, map_to_canonical_strength),
            "personality_fit": map_tags(raw_personalities, map_to_canonical_personality),
            "language_codes": match_langs,
            "math_intensive": bool(matching_raw.get("math_intensive", False)),
            "creative_component": bool(matching_raw.get("creative_component", False)),
            "research_oriented": bool(matching_raw.get("research_oriented", False)),
            "international_potential": bool(matching_raw.get("international_potential", False)),
            "entry_exam_required": bool(matching_raw.get("entry_exam_required", entry_exam)),
            "difficulty_level": normalize_difficulty(matching_raw.get("difficulty_level", "medium")),
            "postgrad_pathway": bool(matching_raw.get("postgrad_pathway", True)),
            "teamwork_oriented": matching_raw.get("teamwork") in ("team", "both", None),
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT B — rtu_bmf_programs.json (BMF professional)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_bmf(r: dict, src: str) -> dict:
    logistics = r.get("logistics", {}) or {}
    finances = r.get("finances", {}) or {}
    admission = r.get("admission", {}) or {}
    degree = r.get("degree", {}) or {}
    career = r.get("career", {}) or {}
    matching_raw = r.get("matching", {}) or {}

    # BMF may use "languages" (plural) instead of "language"
    languages_raw = logistics.get("languages") or logistics.get("language") or []
    lang_codes = normalize_languages(languages_raw)

    # duration_years may be int OR {"full_time": 4, "part_time": 5}
    duration = extract_duration(logistics.get("duration_years", 4))

    # budget may be dict {city: count}
    budget = extract_budget_places(finances.get("budget_places"))

    # fee may be int OR {"full_time": 3500}
    fee = extract_fee(finances.get("annual_fee_eur"))

    entry_exam = bool(
        admission.get("entry_exam")
        or admission.get("requires_entrance_exam", False)
        or matching_raw.get("entry_exam_required", False)
    )
    exam_details = admission.get("entry_exam_details") or ""

    raw_domains = matching_raw.get("interest_domains", [])
    raw_strengths = matching_raw.get("required_strengths", [])
    raw_personalities = matching_raw.get("personality_fit", [])
    raw_lang = matching_raw.get("language_of_instruction", [])
    raw_sectors = career.get("sectors", [])

    sectors_canonical = map_tags(raw_sectors, map_to_canonical_sector)
    match_langs = normalize_languages(raw_lang) if raw_lang else lang_codes

    locations = logistics.get("locations", []) or [logistics.get("start_location", "Rīga")]

    prog_dir = r.get("program_director", {}) or {}
    director_str = f"{prog_dir.get('name', '')} — {prog_dir.get('title', '')}".strip(" —")

    degree_title = flatten_str(degree.get("title") or degree.get("professional_qualification") or "")
    degree_title_en = flatten_str(degree.get("title_en") or "")

    math_int = bool(matching_raw.get("math_intensive", False))
    creative = bool(matching_raw.get("creative_component", False))
    difficulty = normalize_difficulty(matching_raw.get("difficulty_level", "medium"))

    return {
        "id": r.get("id", r.get("code", "")),
        "name": r.get("name", ""),
        "name_en": r.get("name_en", ""),
        "faculty": r.get("faculty", ""),
        "faculty_short": r.get("faculty_short", "BMF"),
        "program_type": r.get("program_type", ""),
        "study_direction": r.get("study_direction", ""),
        "study_field": r.get("study_field", ""),
        "degree": {
            "title": degree_title,
            "title_en": degree_title_en,
            "level": coerce_int(degree.get("ekf_level") or degree.get("level", 6)),
            "professional_qualification": degree.get("professional_qualification"),
        },
        "duration_years": duration,
        "credits": coerce_int(r.get("credits") or logistics.get("credits", 240)),
        "format": (", ".join(logistics.get("formats", [])) or logistics.get("format", "Pilna laika")),
        "languages": lang_codes,
        "locations": locations,
        "budget_places": budget,
        "annual_fee_eur": fee,
        "entry_exam": entry_exam,
        "entry_exam_details": exam_details,
        "description": r.get("description", ""),
        "goals": flatten_str(r.get("goals", "")),
        "url": r.get("url"),
        "program_director": director_str,
        "career": {
            "description": career.get("description", ""),
            "job_titles": career.get("job_titles", []),
            "sectors": raw_sectors,
            "sectors_canonical": sectors_canonical,
        },
        "keywords": [],
        "source_file": src,
        "matching": {
            "interest_domains": map_tags(raw_domains, map_to_canonical_domain),
            "required_strengths": map_tags(raw_strengths, map_to_canonical_strength),
            "personality_fit": map_tags(raw_personalities, map_to_canonical_personality),
            "language_codes": match_langs,
            "math_intensive": math_int,
            "creative_component": creative,
            "research_oriented": bool(matching_raw.get("research_oriented", False)),
            "international_potential": bool(
                matching_raw.get("international_certification")
                or matching_raw.get("international_potential", False)
            ),
            "entry_exam_required": entry_exam,
            "difficulty_level": difficulty,
            "postgrad_pathway": bool(matching_raw.get("postgrad_pathway", True)),
            "teamwork_oriented": True,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT C — DITEF/IVF (matching_profile, study_forms array)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_ditef(r: dict, src: str) -> dict:
    mp = r.get("matching_profile", {}) or {}
    study_forms = r.get("study_forms", []) or []

    # Name: can be dict {lv, en} or plain string
    name_field = r.get("name", {})
    name = flatten_str(name_field) if isinstance(name_field, dict) else (name_field or "")
    name_en = (
        r.get("name_en", "")
        or (name_field.get("en", "") if isinstance(name_field, dict) else "")
    )

    # Faculty: can be dict {name_lv, name_en, abbreviation}
    fac_field = r.get("faculty", {})
    if isinstance(fac_field, dict):
        faculty = fac_field.get("name_lv", "") or fac_field.get("name_en", "")
        faculty_short = fac_field.get("abbreviation", "")
    else:
        faculty = str(fac_field)
        faculty_short = ""

    lang_codes = normalize_languages(r.get("languages", []))

    # study_forms: pick full-time (FT) first, else first available
    ft_forms = [f for f in study_forms if f.get("code") == "FT"] or study_forms
    duration = int(ft_forms[0].get("duration_years", 4)) if ft_forms else 4
    fee = extract_fee(ft_forms[0].get("annual_fee_eur") if ft_forms else None)

    # budget_places: list of {location, count}
    budget = extract_budget_places(r.get("budget_places"))

    entry_exam_obj = r.get("entry_exam", {}) or {}
    if isinstance(entry_exam_obj, dict):
        entry_exam = bool(entry_exam_obj.get("required", False))
        exam_details = entry_exam_obj.get("details", "")
    else:
        entry_exam = bool(entry_exam_obj)
        exam_details = ""

    locations_set: set[str] = set()
    for sf in study_forms:
        locations_set.update(sf.get("locations", []))
    if not locations_set:
        locations_set.add("Rīga")

    # degree
    deg_field = r.get("degree", {})
    if isinstance(deg_field, dict):
        degree_title = deg_field.get("lv", "") or deg_field.get("en", "")
        degree_title_en = deg_field.get("en", "")
    else:
        degree_title = str(deg_field)
        degree_title_en = ""

    # study_direction / study_field
    sdir = r.get("study_direction", {})
    sfield = r.get("study_field", {})
    study_direction = flatten_str(sdir) if isinstance(sdir, dict) else str(sdir or "")
    study_field = flatten_str(sfield) if isinstance(sfield, dict) else str(sfield or "")

    # Career
    career_raw = r.get("career", {}) or {}
    job_titles = career_raw.get("roles", career_raw.get("job_titles", []))
    raw_sectors = career_raw.get("sectors", [])
    sectors_canonical = map_tags(raw_sectors, map_to_canonical_sector)

    # Matching from matching_profile
    primary_domains = mp.get("primary_domains", []) or []
    secondary_domains = mp.get("secondary_domains", []) or []
    all_domains = primary_domains + secondary_domains

    strengths_needed = mp.get("subject_strengths_needed", []) or []
    skill_interests = mp.get("skill_interests", []) or []
    all_strengths = strengths_needed + skill_interests

    personality = mp.get("personality_fit", []) or []

    math_int_raw = coerce_int(mp.get("math_intensity", 2))
    math_intensive = math_int_raw >= 3

    research_int_raw = coerce_int(mp.get("research_intensity", 2))
    research_oriented = research_int_raw >= 3

    intl_raw = coerce_int(mp.get("international_exposure", 1))
    international_potential = intl_raw >= 3

    # Infer creative from domain names
    creative = any(
        kw in str(all_domains).lower()
        for kw in ("design", "art", "creative", "media", "architecture", "visual")
    )

    # Difficulty from average math + tech intensities
    tech_int = coerce_int(mp.get("tech_intensity", math_int_raw))
    avg = (math_int_raw + tech_int) / 2
    difficulty = normalize_difficulty(str(avg))

    keywords_lv = r.get("keywords_lv", []) or []
    keywords_en = r.get("keywords_en", []) or []

    pd_field = r.get("program_director", {}) or {}
    if isinstance(pd_field, dict):
        director_str = f"{pd_field.get('name', '')} — {pd_field.get('title', '')}".strip(" —")
    else:
        director_str = str(pd_field)

    return {
        "id": r.get("id", ""),
        "name": name,
        "name_en": name_en,
        "faculty": faculty,
        "faculty_short": faculty_short,
        "program_type": r.get("program_type", ""),
        "study_direction": study_direction,
        "study_field": study_field,
        "degree": {
            "title": degree_title,
            "title_en": degree_title_en,
            "level": 6,
            "professional_qualification": None,
        },
        "duration_years": duration,
        "credits": coerce_int(r.get("credit_points", 240)),
        "format": "Pilna laika",
        "languages": lang_codes,
        "locations": sorted(locations_set),
        "budget_places": budget,
        "annual_fee_eur": fee,
        "entry_exam": entry_exam,
        "entry_exam_details": exam_details,
        "description": r.get("goal", r.get("description", "")),
        "goals": flatten_str(r.get("goal", "")),
        "url": r.get("url"),
        "program_director": director_str,
        "career": {
            "description": career_raw.get("description", ""),
            "job_titles": job_titles,
            "sectors": raw_sectors,
            "sectors_canonical": sectors_canonical,
        },
        "keywords": keywords_lv + keywords_en,
        "source_file": src,
        "matching": {
            "interest_domains": map_tags(all_domains, map_to_canonical_domain),
            "required_strengths": map_tags(all_strengths, map_to_canonical_strength),
            "personality_fit": map_tags(personality, map_to_canonical_personality),
            "language_codes": lang_codes,
            "math_intensive": math_intensive,
            "creative_component": creative,
            "research_oriented": research_oriented,
            "international_potential": international_potential,
            "entry_exam_required": entry_exam,
            "difficulty_level": difficulty,
            "postgrad_pathway": True,
            "teamwork_oriented": "collaborative" in [p.lower() for p in personality],
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT D — Rezekne/Liepaja/Jura academies (recommendation_metadata)
# ─────────────────────────────────────────────────────────────────────────────

def _norm_rezekne(r: dict, src: str) -> dict:
    institution = r.get("institution", {}) or {}
    program_details = r.get("program_details", {}) or {}
    admission = r.get("admission", {}) or {}
    study_forms = r.get("study_forms", []) or []
    degree_raw = r.get("degree", {}) or {}
    rec_meta = r.get("recommendation_metadata", {}) or {}
    intl = r.get("international", {}) or {}
    career_raw = r.get("career_prospects", r.get("career", {})) or {}

    # Name: can be name_lv/name_en or name.lv/name.en
    name_field = r.get("name", None)
    if isinstance(name_field, dict):
        name = name_field.get("lv", "") or name_field.get("en", "")
        name_en = name_field.get("en", "")
    else:
        name = r.get("name_lv", "") or (name_field if isinstance(name_field, str) else "")
        name_en = r.get("name_en", "")

    # Faculty / institution
    faculty = (
        institution.get("unit", "")
        or r.get("faculty", "")
        or program_details.get("faculty", "")
    )
    city = institution.get("city", "Rīga")

    lang_codes = normalize_languages(admission.get("languages_of_instruction", []) or ["lv"])

    # study_forms: pick full-time first
    ft_forms = [f for f in study_forms if "pilna" in str(f.get("form", "")).lower()] or study_forms
    duration = extract_duration(ft_forms[0].get("duration_years", 4)) if ft_forms else 4
    fee_raw = ft_forms[0].get("tuition_per_year_eur") if ft_forms else None
    fee = extract_fee(fee_raw)
    budget = sum(coerce_int(f.get("budget_places", 0)) for f in study_forms)

    entry_exam = bool(admission.get("requires_entrance_exam", False))
    exam_details = admission.get("entrance_exam_details") or ""

    # Degree
    degree_title = flatten_str(degree_raw.get("degree_lv") or degree_raw.get("degree_en") or "")
    degree_title_en = flatten_str(degree_raw.get("degree_en") or "")
    qual = degree_raw.get("qualification_lv") or degree_raw.get("qualification_en")

    study_direction = (
        program_details.get("study_direction", "")
        or r.get("study_direction", "")
    )
    study_field = (
        program_details.get("study_field", "")
        or r.get("study_field", "")
    )

    # Career
    job_titles = career_raw.get("example_roles", career_raw.get("job_titles", []))
    raw_sectors = career_raw.get("sectors", [])
    sectors_canonical = map_tags(raw_sectors, map_to_canonical_sector)

    # Matching from recommendation_metadata
    interest_tags = rec_meta.get("interest_tags", []) or []
    personality_raw = rec_meta.get("personality_fit", []) or []

    math_str = rec_meta.get("math_intensity", "videja") or "videja"
    math_intensive = normalize_difficulty(math_str) in ("medium_high", "high")

    creativity_str = rec_meta.get("creativity_intensity", "zema") or "zema"
    creative = normalize_difficulty(creativity_str) in ("medium_high", "high")

    difficulty = normalize_difficulty(rec_meta.get("difficulty_relative", "videja"))

    research_str = rec_meta.get("science_intensity", "zema") or "zema"
    research_oriented = normalize_difficulty(research_str) in ("medium_high", "high")

    international_potential = bool(
        intl.get("erasmus_available")
        or intl.get("foreign_lecturers")
        or intl.get("international_study_possible")
    )

    # If no rec_meta, try matching section (some rezekne entries have matching)
    matching_raw = r.get("matching", {}) or {}
    if not interest_tags and matching_raw.get("interest_domains"):
        interest_tags = matching_raw.get("interest_domains", [])
    if not personality_raw and matching_raw.get("personality_fit"):
        personality_raw = matching_raw.get("personality_fit", [])

    # Keywords from description for enrichment
    description = r.get("description", "")
    goals_raw = r.get("goals", []) or r.get("goal", "")
    goals_str = flatten_str(goals_raw)

    prog_dir = r.get("director", {}) or {}
    if isinstance(prog_dir, dict):
        director_str = f"{prog_dir.get('name', '')} — {prog_dir.get('title', '')}".strip(" —")
    else:
        director_str = str(prog_dir)

    specializations = r.get("specializations", []) or []

    return {
        "id": r.get("id", r.get("slug", "")),
        "name": name,
        "name_en": name_en,
        "faculty": faculty,
        "faculty_short": institution.get("abbreviation", ""),
        "program_type": program_details.get("type", r.get("program_type", "")),
        "study_direction": study_direction,
        "study_field": study_field,
        "degree": {
            "title": degree_title,
            "title_en": degree_title_en,
            "level": coerce_int(degree_raw.get("lki_level", 6)),
            "professional_qualification": qual,
        },
        "duration_years": duration,
        "credits": coerce_int(r.get("credits", 240)),
        "format": (ft_forms[0].get("form", "Pilna laika") if ft_forms else "Pilna laika"),
        "languages": lang_codes,
        "locations": [city],
        "budget_places": budget,
        "annual_fee_eur": fee,
        "entry_exam": entry_exam,
        "entry_exam_details": exam_details,
        "description": description,
        "goals": goals_str,
        "url": program_details.get("url", r.get("url")),
        "program_director": director_str,
        "career": {
            "description": career_raw.get("description", ""),
            "job_titles": job_titles,
            "sectors": raw_sectors,
            "sectors_canonical": sectors_canonical,
        },
        "keywords": specializations,
        "source_file": src,
        "matching": {
            "interest_domains": map_tags(interest_tags, map_to_canonical_domain),
            "required_strengths": map_tags(
                matching_raw.get("required_strengths", []), map_to_canonical_strength
            ),
            "personality_fit": map_tags(personality_raw, map_to_canonical_personality),
            "language_codes": lang_codes,
            "math_intensive": math_intensive,
            "creative_component": creative,
            "research_oriented": research_oriented,
            "international_potential": international_potential,
            "entry_exam_required": entry_exam,
            "difficulty_level": difficulty,
            "postgrad_pathway": bool(career_raw.get("can_continue_masters", True)),
            "teamwork_oriented": True,
        },
    }
