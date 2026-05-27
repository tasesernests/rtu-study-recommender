"""
RTU Study Programme AI Recommender
scoring.py — Weighted, explainable recommendation engine.

Scoring philosophy:
  - Every student input dimension has a corresponding programme dimension
  - Points are awarded for matches, penalties for incompatibilities
  - Score is normalised to 0–100% based on what the student selected
  - A full scoring_breakdown is returned alongside the score for AI explainability
"""

from typing import Any
from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS,
    get_label, normalize_difficulty,
)

# ─────────────────────────────────────────────────────────────────────────────
# SCORING WEIGHTS
# ─────────────────────────────────────────────────────────────────────────────
W_INTEREST = 4        # per matched interest domain
W_STRENGTH = 3        # per matched strength / subject
W_SKILL = 3           # per matched skill (reuses strength bucket)
W_PERSONALITY = 2     # per matched personality trait
W_SECTOR = 3          # per matched industry sector
W_LANGUAGE = 2        # language available match
W_DIFFICULTY = 2      # difficulty preference match
W_RESEARCH = 2        # research-orientation match
W_INTERNATIONAL = 2   # international opportunity match
W_CREATIVE = 2        # creative component match
W_MATH = 2            # math-intensity match
W_EXAM = 2            # entrance exam compatibility
W_TEAMWORK = 1        # teamwork preference match
W_CAREER_TEXT = 3     # career-text keyword alignment bonus

# Minimum denominator — prevents blank / sparse profiles from inflating scores.
_MIN_MAX_POSSIBLE = 25

# ─────────────────────────────────────────────────────────────────────────────
# DOMAIN & STRENGTH AFFINITY
# ─────────────────────────────────────────────────────────────────────────────
# When a student's interest/strength doesn't exactly match a programme tag but
# is semantically related, award partial credit.

_DOMAIN_AFFINITY: dict[str, list[str]] = {
    "it_programming":             ["data_science_ai", "software_engineering", "electronics_telecom", "robotics_automation"],
    "data_science_ai":            ["it_programming", "software_engineering"],
    "software_engineering":       ["it_programming", "data_science_ai"],
    "electronics_telecom":        ["it_programming", "robotics_automation", "energy_power"],
    "robotics_automation":        ["electronics_telecom", "mechanics_engineering", "it_programming"],
    "mechanics_engineering":      ["robotics_automation", "energy_power", "transport_aviation"],
    "transport_aviation":         ["mechanics_engineering", "robotics_automation", "maritime"],
    "construction_civil":         ["architecture", "environment_sustainability", "mechanics_engineering"],
    "architecture":               ["construction_civil", "art_design"],
    "art_design":                 ["architecture"],
    "chemistry_biotech":          ["environment_sustainability", "medical_technology"],
    "environment_sustainability": ["chemistry_biotech", "energy_power", "construction_civil"],
    "energy_power":               ["environment_sustainability", "electronics_telecom", "mechanics_engineering"],
    "medical_technology":         ["chemistry_biotech", "education_research"],
    "business_management":        ["data_science_ai", "education_research"],
    "education_research":         ["business_management", "medical_technology"],
    "maritime":                   ["transport_aviation", "mechanics_engineering"],
}
_AFFINITY_FACTOR = 0.35          # 35 % of W_INTEREST per related-domain hit

_STRENGTH_AFFINITY: dict[str, list[str]] = {
    "mathematics":         ["physics", "analytical_thinking"],
    "physics":             ["mathematics", "technical_thinking"],
    "programming":         ["analytical_thinking", "technical_thinking"],
    "analytical_thinking": ["mathematics", "research"],
    "technical_thinking":  ["physics", "practical_skills"],
    "creativity":          ["drawing_design"],
    "drawing_design":      ["creativity"],
    "research":            ["analytical_thinking"],
    "economics_finance":   ["analytical_thinking"],
}
_STRENGTH_AFFINITY_FACTOR = 0.30  # 30 % of W_STRENGTH per related-strength hit

# Career text keyword → interest domain hints  (local semantic matching)
_CAREER_HINTS: list[tuple[str, str]] = [
    ("software",    "it_programming"),   ("coding",       "it_programming"),
    ("developer",   "it_programming"),   ("programmer",   "it_programming"),
    ("web dev",     "it_programming"),   ("cyber",        "it_programming"),
    ("network",     "it_programming"),   ("cloud",        "it_programming"),
    ("ai ",         "data_science_ai"),  ("machine learn","data_science_ai"),
    (" data ",      "data_science_ai"),  ("neural",       "data_science_ai"),
    ("artificial intelligence", "data_science_ai"),
    ("robot",       "robotics_automation"), ("automat",   "robotics_automation"),
    ("mechatron",   "robotics_automation"),
    ("electronic",  "electronics_telecom"), ("telecom",   "electronics_telecom"),
    ("power grid",  "energy_power"),     ("solar",        "energy_power"),
    ("wind energy", "energy_power"),     ("renewable",    "environment_sustainability"),
    ("architect",   "architecture"),     ("urban plan",   "architecture"),
    ("construction","construction_civil"),("civil eng",   "construction_civil"),
    (" design",     "art_design"),       ("graphic",      "art_design"),
    ("visual art",  "art_design"),       ("illustration", "art_design"),
    ("chemical",    "chemistry_biotech"),("chemistry",    "chemistry_biotech"),
    ("biotech",     "chemistry_biotech"),("pharma",       "chemistry_biotech"),
    ("environment", "environment_sustainability"), ("climate",  "environment_sustainability"),
    ("sustainab",   "environment_sustainability"),
    ("transport",   "transport_aviation"), ("aviation",   "transport_aviation"),
    ("pilot",       "transport_aviation"), ("aircraft",   "transport_aviation"),
    ("logistic",    "transport_aviation"),
    ("ship eng",    "maritime"),         ("marine eng",   "maritime"),
    ("navigation",  "maritime"),         ("naval",        "maritime"),
    ("business",    "business_management"), ("management","business_management"),
    ("entrepreneur","business_management"), ("finance",   "business_management"),
    ("econom",      "business_management"), ("marketing", "business_management"),
    ("mechanic",    "mechanics_engineering"), ("manufactur","mechanics_engineering"),
    ("industrial eng","mechanics_engineering"),
    ("medical",     "medical_technology"), ("biomedical", "medical_technology"),
    ("health tech", "medical_technology"),
    ("research",    "education_research"), ("scientist",  "education_research"),
    ("teaching",    "education_research"),
]

# Penalties (applied after normalisation, as percentage-point deductions)
P_LANGUAGE = 20       # preferred language not offered (large — deal-breaker)
P_EXAM = 15           # student avoids exams but programme requires one
P_DIFFICULTY_HARD = 10  # student wants easy but programme is hard
P_MATH = 8            # student dislikes maths but programme is math-intensive


# ─────────────────────────────────────────────────────────────────────────────
# CAREER TEXT BONUS SCORER
# ─────────────────────────────────────────────────────────────────────────────

def _career_text_bonus(career_text: str, programme: dict) -> float:
    """
    Award raw bonus points when student career-text keywords align with
    programme domains.  Uses _CAREER_HINTS + domain-affinity expansion.
    Returns float in [0, W_CAREER_TEXT].
    """
    if not career_text or len(career_text.strip()) < 10:
        return 0.0
    text      = f" {career_text.lower()} "
    m         = programme.get("matching", {}) or {}
    p_domains = set(m.get("interest_domains", []))

    hinted: set[str] = set()
    for kw, domain in _CAREER_HINTS:
        if kw in text:
            hinted.add(domain)

    # Expand via affinity so adjacent domains also count (at reduced weight)
    expanded: set[str] = set(hinted)
    for d in hinted:
        for rel in _DOMAIN_AFFINITY.get(d, []):
            expanded.add(rel)

    domain_hits = len(expanded & p_domains)
    return min(domain_hits * (W_CAREER_TEXT / 3.0), float(W_CAREER_TEXT))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCORING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def score_programme(student: dict, programme: dict) -> tuple[float, dict]:
    """
    Calculate compatibility between a student profile and a programme.

    Args:
        student:   Normalised student profile dict (from UI form)
        programme: Normalised programme dict (from data_loader)

    Returns:
        (compatibility_pct, breakdown_dict)
        - compatibility_pct: float 0.0–100.0
        - breakdown_dict: detailed scoring explanation for display + AI prompt
    """
    m = programme.get("matching", {}) or {}
    breakdown: dict[str, Any] = {}
    raw_score = 0
    max_positive = 0

    # ── 1. INTEREST DOMAINS (exact match + affinity partial credit) ──────────
    s_interests       = set(student.get("interests", []))
    p_interests       = set(m.get("interest_domains", []))
    matched_interests = s_interests & p_interests

    pts_i = len(matched_interests) * W_INTEREST
    # Related-domain partial credit: 35 % per affinity hit
    affinity_interests: list[str] = [
        si for si in (s_interests - matched_interests)
        if set(_DOMAIN_AFFINITY.get(si, [])) & p_interests
    ]
    pts_i += len(affinity_interests) * W_INTEREST * _AFFINITY_FACTOR

    max_i         = len(s_interests) * W_INTEREST
    raw_score    += pts_i
    max_positive += max_i
    breakdown["interests"] = {
        "student":   list(s_interests),
        "programme": list(p_interests),
        "matched":   list(matched_interests),
        "affinity":  affinity_interests,
        "points":    round(pts_i, 2),
        "max":       max_i,
        "weight":    W_INTEREST,
        "label":     "Interešu jomas",
    }

    # ── 2. STRENGTHS / SUBJECTS (exact + affinity partial credit) ────────────
    s_strengths       = set(student.get("strengths", []))
    p_strengths       = set(m.get("required_strengths", []))
    matched_strengths = s_strengths & p_strengths

    pts_s = len(matched_strengths) * W_STRENGTH
    # Related-strength partial credit: 30 % per affinity hit
    affinity_strengths: list[str] = [
        ss for ss in (s_strengths - matched_strengths)
        if set(_STRENGTH_AFFINITY.get(ss, [])) & p_strengths
    ]
    pts_s += len(affinity_strengths) * W_STRENGTH * _STRENGTH_AFFINITY_FACTOR

    max_s         = len(s_strengths) * W_STRENGTH
    raw_score    += pts_s
    max_positive += max_s
    breakdown["strengths"] = {
        "student":   list(s_strengths),
        "programme": list(p_strengths),
        "matched":   list(matched_strengths),
        "affinity":  affinity_strengths,
        "points":    round(pts_s, 2),
        "max":       max_s,
        "weight":    W_STRENGTH,
        "label":     "Stiprās puses & Priekšmeti",
    }

    # ── 3. PERSONALITY TRAITS ────────────────────────────────────────────────
    s_personality = set(student.get("personality", []))
    p_personality = set(m.get("personality_fit", []))
    matched_personality = s_personality & p_personality
    pts = len(matched_personality) * W_PERSONALITY
    max_p = len(s_personality) * W_PERSONALITY
    raw_score += pts
    max_positive += max_p
    breakdown["personality"] = {
        "student": list(s_personality),
        "programme": list(p_personality),
        "matched": list(matched_personality),
        "points": pts,
        "max": max_p,
        "weight": W_PERSONALITY,
        "label": "Personības tipa atbilstība",
    }

    # ── 4. INDUSTRY SECTORS ───────────────────────────────────────────────────
    s_sectors = set(student.get("sectors", []))
    p_sectors = set(programme.get("career", {}).get("sectors_canonical", []))
    matched_sectors = s_sectors & p_sectors
    pts = len(matched_sectors) * W_SECTOR
    max_sec = len(s_sectors) * W_SECTOR
    raw_score += pts
    max_positive += max_sec
    breakdown["sectors"] = {
        "student": list(s_sectors),
        "programme": list(p_sectors),
        "matched": list(matched_sectors),
        "points": pts,
        "max": max_sec,
        "weight": W_SECTOR,
        "label": "Nozares preferences",
    }

    # ── 5. LANGUAGE ───────────────────────────────────────────────────────────
    s_lang = student.get("preferred_language", "lv")
    p_langs = set(m.get("language_codes", ["lv"]))
    lang_match = s_lang in p_langs
    breakdown["language"] = {
        "student_pref": s_lang,
        "programme_langs": list(p_langs),
        "match": lang_match,
        "points": W_LANGUAGE if lang_match else 0,
        "max": W_LANGUAGE,
        "weight": W_LANGUAGE,
        "label": "Studiju valoda",
    }
    raw_score += W_LANGUAGE if lang_match else 0
    max_positive += W_LANGUAGE

    # ── 6. DIFFICULTY ──────────────────────────────────────────────────────────
    s_difficulty = student.get("preferred_difficulty", "medium")
    p_difficulty = m.get("difficulty_level", "medium")
    diff_match = _difficulty_compatible(s_difficulty, p_difficulty)
    diff_pts = W_DIFFICULTY if diff_match else 0
    raw_score += diff_pts
    max_positive += W_DIFFICULTY
    breakdown["difficulty"] = {
        "student_pref": s_difficulty,
        "programme": p_difficulty,
        "compatible": diff_match,
        "points": diff_pts,
        "max": W_DIFFICULTY,
        "label": "Grūtības pakāpe",
    }

    # ── 7. RESEARCH ORIENTATION ───────────────────────────────────────────────
    # Dimension is only included in scoring when the student actively expressed
    # the preference (toggle=True).  When student=False the toggle was left at
    # its default — no opinion → exclude from both numerator AND denominator so
    # a blank profile cannot accumulate free half-points here.
    s_research = bool(student.get("research_oriented", False))
    p_research = bool(m.get("research_oriented", False))
    if s_research:
        research_pts  = W_RESEARCH if p_research else 0
        raw_score    += research_pts
        max_positive += W_RESEARCH
        _research_max = W_RESEARCH
    else:
        research_pts  = 0
        _research_max = 0   # excluded — no preference expressed
    breakdown["research"] = {
        "student": s_research,
        "programme": p_research,
        "points": research_pts,
        "max": _research_max,
        "label": "Pētnieciskā orientācija",
    }

    # ── 8. INTERNATIONAL ──────────────────────────────────────────────────────
    # Same principle: only score when student actively wants international study.
    s_intl = bool(student.get("international", False))
    p_intl = bool(m.get("international_potential", False))
    if s_intl:
        intl_pts     = W_INTERNATIONAL if p_intl else 0
        raw_score   += intl_pts
        max_positive += W_INTERNATIONAL
        _intl_max    = W_INTERNATIONAL
    else:
        intl_pts  = 0
        _intl_max = 0
    breakdown["international"] = {
        "student": s_intl,
        "programme": p_intl,
        "points": intl_pts,
        "max": _intl_max,
        "label": "Starptautiskās iespējas",
    }

    # ── 9. CREATIVE COMPONENT ────────────────────────────────────────────────
    # Same principle: only score when student enjoys creative / design work.
    s_creative = bool(student.get("creative", False))
    p_creative = bool(m.get("creative_component", False))
    if s_creative:
        creative_pts  = W_CREATIVE if p_creative else 0
        raw_score    += creative_pts
        max_positive += W_CREATIVE
        _creative_max = W_CREATIVE
    else:
        creative_pts  = 0
        _creative_max = 0
    breakdown["creative"] = {
        "student": s_creative,
        "programme": p_creative,
        "points": creative_pts,
        "max": _creative_max,
        "label": "Radošā / dizaina komponente",
    }

    # ── 10. MATH INTENSITY ────────────────────────────────────────────────────
    s_math = bool(student.get("math_friendly", False))
    p_math = bool(m.get("math_intensive", False))
    math_pts = W_MATH if (s_math and p_math) else (W_MATH if (not s_math and not p_math) else 0)
    raw_score += math_pts
    max_positive += W_MATH
    breakdown["math"] = {
        "student_likes_math": s_math,
        "programme_math_intensive": p_math,
        "points": math_pts,
        "max": W_MATH,
        "label": "Matemātikas intensitāte",
    }

    # ── 11. ENTRANCE EXAM ─────────────────────────────────────────────────────
    s_exam_ok = bool(student.get("exam_ok", True))
    p_exam_req = bool(m.get("entry_exam_required", False))
    if p_exam_req and s_exam_ok:
        exam_pts = W_EXAM
    elif not p_exam_req:
        exam_pts = W_EXAM
    else:
        exam_pts = 0  # student doesn't want exam, but it's required
    raw_score += exam_pts
    max_positive += W_EXAM
    breakdown["exam"] = {
        "student_ok_with_exam": s_exam_ok,
        "programme_requires_exam": p_exam_req,
        "compatible": exam_pts > 0,
        "points": exam_pts,
        "max": W_EXAM,
        "label": "Iestājpārbaudījums",
    }

    # ── 12. TEAMWORK ─────────────────────────────────────────────────────────
    s_team = student.get("teamwork", "both")
    p_team = bool(m.get("teamwork_oriented", True))
    team_match = s_team in ("team", "both") or not p_team
    team_pts = W_TEAMWORK if team_match else 0
    raw_score += team_pts
    max_positive += W_TEAMWORK
    breakdown["teamwork"] = {
        "student_pref": s_team,
        "programme_teamwork": p_team,
        "points": team_pts,
        "max": W_TEAMWORK,
        "label": "Komandas darbs",
    }

    # ── 13. CAREER TEXT BONUS ─────────────────────────────────────────────────
    # The student's free-text career goal is matched against programme domains
    # (using keyword hints + affinity expansion).  Only counted in the
    # denominator when there is substantive text (≥ 10 chars).
    career_text  = (student.get("career_text") or "").strip()
    career_bonus = _career_text_bonus(career_text, programme)
    raw_score   += career_bonus
    # Career text is a pure additive bonus — it NEVER increases the denominator,
    # so it can only raise scores (or be neutral when 0).  This ensures students
    # are not penalised for filling in the career goal field.
    breakdown["career_text"] = {
        "bonus": round(career_bonus, 2),
        "max":   W_CAREER_TEXT,
        "label": "Karjeras mērķi",
    }

    # ── 14. DEEP MATCH BONUS ──────────────────────────────────────────────────
    # Reward strong cross-dimension alignment: when both interests AND strengths
    # match well, the programme is a genuinely excellent fit — give a confidence
    # boost that helps it clearly separate from weaker alternatives.
    n_i        = len(matched_interests)
    n_s        = len(matched_strengths)
    deep_bonus = (
        W_INTEREST if (n_i >= 3 and n_s >= 2) else  # strong fit: +4 pts
        W_STRENGTH if (n_i >= 2 and n_s >= 2) else  # good fit:   +3 pts
        0
    )
    raw_score                     += deep_bonus
    breakdown["deep_match_bonus"]  = deep_bonus

    # ── NORMALISE TO PERCENTAGE ───────────────────────────────────────────────
    # Apply a minimum denominator floor so that sparse / blank profiles cannot
    # inflate their percentage via a tiny max_possible.
    # A blank profile accumulates ~9 pts (language + difficulty + math + exam +
    # teamwork).  Without floor: 9/9 = 100%.  With floor=25: 9/25 = 36%.
    profile_sparse = max_positive < _MIN_MAX_POSSIBLE
    effective_max  = max(max_positive, _MIN_MAX_POSSIBLE)
    base_pct       = (raw_score / effective_max) * 100.0

    # ── PENALTIES ─────────────────────────────────────────────────────────────
    penalty = 0
    penalties_applied = []

    if not lang_match and s_lang != "any":
        penalty += P_LANGUAGE
        penalties_applied.append(f"Vēlamā valoda ({LANG_LABELS.get(s_lang, s_lang)}) nav pieejama (−{P_LANGUAGE}%)")

    if not s_exam_ok and p_exam_req:
        penalty += P_EXAM
        penalties_applied.append(f"Nepieciešams iestājpārbaudījums (−{P_EXAM}%)")

    if _difficulty_too_hard(s_difficulty, p_difficulty):
        penalty += P_DIFFICULTY_HARD
        penalties_applied.append(f"Programma ir grūtāka nekā vēlams (−{P_DIFFICULTY_HARD}%)")

    if not s_math and p_math:
        penalty += P_MATH
        penalties_applied.append(f"Matemātikas intensīvā programma neatbilst (−{P_MATH}%)")

    breakdown["penalties"]      = penalties_applied
    breakdown["raw_score"]      = round(raw_score, 2)
    breakdown["max_possible"]   = round(effective_max, 2)   # includes floor
    breakdown["profile_sparse"] = profile_sparse            # UI warning flag
    breakdown["base_pct"]       = round(base_pct, 1)
    breakdown["penalty_pct"]    = penalty

    compatibility = max(0.0, min(100.0, base_pct - penalty))
    breakdown["final_pct"] = round(compatibility, 1)

    return compatibility, breakdown


# ─────────────────────────────────────────────────────────────────────────────
# RANK PROGRAMMES
# ─────────────────────────────────────────────────────────────────────────────

def rank_programmes(
    student: dict,
    programmes: list[dict],
    top_n: int = 3,
    filters: dict | None = None,
) -> list[dict]:
    """
    Score and rank all programmes for a given student profile.

    Args:
        student:    Student profile dict
        programmes: List of normalised programme dicts
        top_n:      Number of top results to return (default 3)
        filters:    Optional dict of UI filters to pre-filter programmes

    Returns:
        List of dicts: [{programme, score, breakdown}, ...] sorted by score desc
    """
    filtered = _apply_filters(programmes, filters or {})

    results = []
    for prog in filtered:
        score, breakdown = score_programme(student, prog)
        results.append({"programme": prog, "score": score, "breakdown": breakdown})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def score_all_programmes(
    student: dict,
    programmes: list[dict],
    filters: dict | None = None,
) -> list[dict]:
    """Score ALL programmes (used for full results / comparison view)."""
    return rank_programmes(student, programmes, top_n=len(programmes), filters=filters)


# ─────────────────────────────────────────────────────────────────────────────
# FILTER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _apply_filters(programmes: list[dict], filters: dict) -> list[dict]:
    """Pre-filter programmes based on sidebar filter selections."""
    result = programmes
    if faculties := filters.get("faculties"):
        result = [p for p in result if p.get("faculty") in faculties]
    if langs := filters.get("languages"):
        result = [
            p for p in result
            if set(p.get("languages", [])) & set(langs)
        ]
    if locations := filters.get("locations"):
        result = [
            p for p in result
            if set(p.get("locations", [])) & set(locations)
        ]
    if prog_types := filters.get("program_types"):
        result = [p for p in result if p.get("program_type") in prog_types]
    if filters.get("no_exam_only"):
        result = [p for p in result if not p.get("matching", {}).get("entry_exam_required", False)]
    if filters.get("budget_only"):
        result = [p for p in result if p.get("budget_places", 0) > 0]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_DIFF_ORDER = {"low": 0, "medium": 1, "medium_high": 2, "high": 3}


def _difficulty_compatible(student_pref: str, programme_level: str) -> bool:
    """True if programme difficulty is within +1 level of student preference."""
    s = _DIFF_ORDER.get(student_pref, 1)
    p = _DIFF_ORDER.get(programme_level, 1)
    return abs(p - s) <= 1


def _difficulty_too_hard(student_pref: str, programme_level: str) -> bool:
    """True if programme is MORE than 1 difficulty tier above student preference."""
    s = _DIFF_ORDER.get(student_pref, 1)
    p = _DIFF_ORDER.get(programme_level, 1)
    return (p - s) > 1


# ─────────────────────────────────────────────────────────────────────────────
# HUMAN-READABLE BREAKDOWN SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def breakdown_summary(breakdown: dict) -> dict:
    """
    Convert raw breakdown dict to human-readable label lists.
    Used by the UI 'Why this score?' section.
    """
    from utils import INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS

    def _labels(keys: list, mapping: dict) -> list[str]:
        return [get_label(mapping, k) for k in keys if k]

    int_bd = breakdown.get("interests", {})
    str_bd = breakdown.get("strengths", {})
    return {
        "matched_interests":  _labels(int_bd.get("matched",  []), INTEREST_DOMAINS),
        "affinity_interests": _labels(int_bd.get("affinity", []), INTEREST_DOMAINS),
        "missed_interests":   _labels(
            list(
                set(int_bd.get("student", []))
                - set(int_bd.get("matched", []))
                - set(int_bd.get("affinity", []))
            ),
            INTEREST_DOMAINS,
        ),
        "matched_strengths":  _labels(str_bd.get("matched",  []), STRENGTH_TAGS),
        "affinity_strengths": _labels(str_bd.get("affinity", []), STRENGTH_TAGS),
        "matched_personality": _labels(breakdown.get("personality", {}).get("matched", []), PERSONALITY_TRAITS),
        "matched_sectors":    _labels(breakdown.get("sectors",    {}).get("matched",  []), INDUSTRY_SECTORS),
        "language_ok":    breakdown.get("language",   {}).get("match",      False),
        "exam_ok":        breakdown.get("exam",       {}).get("compatible",  True),
        "penalties":      breakdown.get("penalties",  []),
        "final_pct":      breakdown.get("final_pct",  0),
        "base_pct":       breakdown.get("base_pct",   0),
        "career_bonus":   breakdown.get("career_text", {}).get("bonus", 0),
        "deep_bonus":     breakdown.get("deep_match_bonus", 0),
    }
